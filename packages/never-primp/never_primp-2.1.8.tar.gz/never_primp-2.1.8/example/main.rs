use std::error::Error;
use html2text::Error::Fail;
use wreq::{Client, Proxy};
use wreq_util::Emulation;
use wreq::redirect::Policy;


async fn redirect_test() -> Result<(), Box<dyn std::error::Error>>{
    let proxy = Proxy::all("http://unmetered.residential.proxyrack.net:10252")?
        .basic_auth("chivalry_jy-country-jp", "EG3JGXL-UUD7ZOC-JVUH4JJ-26QXCIR-LE9YQI7-TMBLUU8-A4ZQWEN");  // 如果 URL 中已嵌入凭证，可省略此行

    let client = Client::builder()
        // .proxy(proxy)
        .emulation(Emulation::Chrome142)  // 可选：添加浏览器仿真
        .redirect(Policy::limited(20)) // 禁用自动跟随，手动处理 302
        .build()?;

    // let mut url = "http://httpbin.org/redirect-to?url=http://httpbin.org/get".to_string();
    let mut url = "https://103.73.160.204:4433".to_string();
    let mut redirect_count = 0;
    let max_redirects = 5;

    loop {
        println!("请求 URL: {}", url);
        let response = client.get(&url).send().await;

        match response {
            Ok(resp) => {
                let status = resp.status();
                println!("响应状态: {}", status);

                if status.is_success() {
                    println!("最终响应体: {}", resp.text().await?);
                    return Ok(());
                } else if status.is_redirection() {
                    if let Some(location) = resp.headers().get("Location") {
                        // let new_url = resp.uri().join()?;
                        let new_url = location.to_str()?;
                        url = new_url.to_string();
                        redirect_count += 1;
                        if redirect_count > max_redirects {
                            return Err("超过最大重定向次数".into());
                        }
                        println!("检测到 302 重定向到: {}", url);
                        continue;  // 继续手动请求新 URL
                    } else {
                        return Err("无 Location 头，无法重定向".into());
                    }
                } else {
                    return Err(format!("意外状态: {}", status).into());
                }
            }
            Err(err) => {
                // 如果是代理认证失败（407），这里会捕获
                return Err(format!("请求失败: {}", err).into());
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // 配置代理（替换为您的实际代理地址和凭证）

    let proxy = Proxy::http("http://127.0.0.1:9000")?;
    let proxys = Proxy::https("https://127.0.0.1:9000")?;

    // 构建客户端，禁用自动重定向
    let client = Client::builder()
        // .proxy(proxy)
        // .proxy(proxys)
        .cert_verification(false)
        .emulation(Emulation::Chrome142)  // 可选：添加浏览器仿真
        .redirect(Policy::limited(20)) // 禁用自动跟随，手动处理 302
        .build()?;

    let result = client.get("https://103.73.160.204:4433".to_string()).send().await;

    match result {
        Ok(resp) => {
            let status = resp.status();
            println!("响应状态: {}", status);
            println!("响应头: {:?}", resp.headers());
            println!("响应体: {}", resp.text().await?);
        }
        Err(err) => {
            println!("请求失败: {}", err);
        }
    }



    Ok(())
}