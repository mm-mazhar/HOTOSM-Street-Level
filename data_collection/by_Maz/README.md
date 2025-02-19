## Data Collection

#### Setting Up Ngrok for Local Development with Mapillary API

1. Install Ngrok
- Download Ngrok: Go to https://ngrok.com/download and download the appropriate Ngrok package for your operating system (Windows, macOS, or Linux).

- Install Ngrok:
    
    - Windows: Unzip the downloaded file. You'll find the ngrok.exe executable inside.
    
    - macOS: Unzip the downloaded file. You'll find the ngrok executable inside. Move it to a convenient location (e.g., /usr/local/bin).

    - Linux: Unzip the downloaded file. You'll find the ngrok executable inside. Make it executable: chmod +x ngrok. Move it to a convenient location (e.g., /usr/local/bin).

- Add to Path (Optional but Recommended): To easily run Ngrok from any terminal, add its directory to your system's PATH environment variable. The method for doing this depends on your OS:

- Windows: Search for "Edit the system environment variables," edit the "Path" variable, and add the directory containing ngrok.exe.

- macOS/Linux: Edit your .bashrc, .zshrc, or other shell configuration file and add the line: export PATH="$PATH:/path/to/ngrok". Replace /path/to/ngrok with the actual directory.

2. Authenticate Ngrok
- Sign up for an Ngrok Account: Go to https://ngrok.com/signup and create a free account.

- Get Authtoken: Log in to your Ngrok account and find your authtoken on the dashboard. It's typically on `Setup & Installation Page`"

- Authenticate Ngrok: In your terminal, run:
    - `ngrok config add-authtoken YOUR_AUTHTOKEN`

3. Run a Local Web Server
- You need a web server to receive the authorization code after Mapillary redirects. Here's how to start a simple one using Python:

- Navigate to your project folder: In your terminal, cd into the directory where you have your Python script for interacting with the Mapillary API.

- Start a Python web server: 
-   - Run the following command:
    - `python -m http.server 8080` 
    - This starts a simple HTTP server on port 8080.

4. Expose Your Local Server with Ngrok
- Go to `https://dashboard.ngrok.com/edges` Page
- Clink on `Create Edge`
- Select `HTTPS`
- Click on `Create Edge`
- You should see an endpoint created

<table style="width:100%" align="left">
  <tr>
    <td><img src="https://i.imgur.com/oA5KpJ2.png" width="900px" height=200px/></td>
    </tr>
</table>

- Copy that endpoint and paste it in as your `REDIRECT_URI` in your `.env` file 
- and also on `https://www.mapillary.com/dashboard/developers`

<table style="width:100%" align="left">
  <tr>
    <td><img src="https://i.imgur.com/lSNruiY.png" width="900px" height=600px/></td>
    </tr>
</table>


- Now Hit `Start a Tunnel`

<table style="width:100%" align="left">
  <tr>
    <td><img src="https://i.imgur.com/JdB4lJd.png" width="900px" height=300px/></td>
    </tr>
</table>

- Copy and Paste the command in your terminal 
- Note: don't forget to replace `80` with `8080` as the port number
- e.g. You copied `ngrok tunnel --label edge=<your-edge-id> http://localhost:80`
- Put `8080` instead of `80` 
- `ngrok tunnel --label edge=<your-edge-id> http://localhost:8080`
- Run the command in another terminal

<table style="width:100%" align="left">
  <tr>
    <td><img src="https://i.imgur.com/qFEToBa.png" width="900px" height=320px/></td>
    </tr>
</table>

5. Run the Python Script

- Now you can run your Python script (in another terminal) that interacts with the Mapillary API.
- e.g `uv run python ./data_collection/by_Maz/get_data.py`
<table style="width:100%" align="left">
  <tr>
    <td><img src="https://i.imgur.com/KohcOUJ.png" width="900px" height=160px/></td>
    </tr>
</table>

- It should be able to receive the authorization code from the Mapillary redirect.
- Now in the browser you should see
- Click Authorize if you are already logged in

<table style="width:100%" align="left">
  <tr>
    <td><img src="https://i.imgur.com/mB4wHYf.png" width="900px" height=350px/></td>
    </tr>
</table>

- then copy the code and paste back in the terminal and hit enter

<table style="width:100%" align="left">
  <tr>
    <td><img src="https://i.imgur.com/2B17kMX.png" width="900px" height=270px/></td>
    </tr>
</table>
- Your script should start downloading images

