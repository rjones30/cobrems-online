# Cobrems Online Tools for the Hall D Beamline

A suite of CGI-based web tools for the HallD Coherent Bramsstrahlung beam. This repository contains Bash entry points that wrap Python worker scripts.

## Repository Structure
* `*.cgi`: Bash gateway scripts (must be executable).
* `*.py`: Python worker scripts containing the core logic.
* `.htaccess`: Local Apache configuration to enable CGI execution.

## Installation & Setup

1. **Clone the repository** into your Apache document root:
   ```bash
   git clone <your-repo-url> /path/to/apache/docs/cobrems
   ```

2. **Set the linux execute bits** on the .py and .cgi scripts.

3. **Set the owner of the work directory** to the uid of the apache webserver.

4. **Add the following permissions** to your apached webserver configuration:
   ```apache
   <Directory "[path-to-installed-directory]">
    AllowOverride All
    Require all granted
   </Directory>
   ```

5. **Restart the apache server**: systemctl restart httpd

6. **Test the tools** using a web browser:
	* `https://[SERVER_IP]/[PATH-TO-INSTALLED-TOOLS]/ratetool.cgi`
	* `https://[SERVER_IP]/[PATH-TO-INSTALLED-TOOLS]/harptool.cgi`
	* `https://[SERVER_IP]/[PATH-TO-INSTALLED-TOOLS]/harptool_2d.cgi`

## Dependencies

1. **ROOT**: you need to have the root command in the path, tested with v6.38.

2. **PAW**: you need to have the CERNLIB 2005 suite installed, so that the pawX11 command is in the path.

3. **vncserver**: you need to have the vncserver installed, so that vncserver is in the path. The ratetool.cgi script starts its on private Xvnc session on display 99 and pawX11 uses it to generate plots through the X11 graphical interface. If screen 99 is not available, change the display number in the code near the top of the ratetool.cgi script.
