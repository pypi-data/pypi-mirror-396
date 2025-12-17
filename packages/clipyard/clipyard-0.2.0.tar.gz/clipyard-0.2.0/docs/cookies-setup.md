Some URLs on YouTube require you to be logged in / work around CAPTCHA in order to be able to download. `yt-dlp` supports passing these cookies to allow downloading, but their documentation is somewhat cumbersome to navigate. This is a simplified guide to doing so in a way that lets you run the script in remote servers you only ssh into.

### Grabbing cookies from YouTube

[Original Source](https://github.com/yt-dlp/yt-dlp/wiki/extractors#exporting-youtube-cookies)
1. Login to YouTube from an incognito window in Google Chrome
2. In the same tab, go to https://www.youtube.com/robots.txt (This should be the only tab open)
3. Open the developer tools (Alt + Cmd + I on macOS), and select the YouTube cookies
4. Save into a text file called `cookies-raw.txt` (filename doesn't matter)

![](./cookies.jpg)

### Convert cookies into Netscape Format

This step is poorly documented in `yt-dlp`'s docs (or I just couldn't find it).

Use [this repo](https://github.com/dandv/convert-chrome-cookies-to-netscape-format) (requires Node.js) to convert the above file into Netscape format. Refer to the that repo's README for details - it's very clearly documented. You should now be able to use this file to pass into the `--cookies` argument
