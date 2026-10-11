# How to check a Simple Astrology App download

Use this when you download Simple Astrology App and want to be sure the file was not changed on the way to your computer. A checksum is a fingerprint of the file. If the download is cut short, or if someone swaps the installer, the fingerprint no longer matches the one published with the download.

The installers and checksums are on the Download section of [crn.net.au/simple-astrology](https://crn.net.au/simple-astrology#download). Each opperating system download button has its SHA-256 checksum directly underneath it.

- Debian Linux: `simple-astrology-app_<version>_amd64.deb`
- Windows: `Simple Astrology App Setup <version>.exe`

`<version>` is the version offered on that page, such as `0.0.1`. Check the file you actually downloaded.

Copy the checksum from under the button for the file you downloaded. SHA-256 is 64 hexadecimal characters. Capital and lowercase letters are the same value. A checksum copied from an email or forum post does not check this download.

## Linux

Open a terminal in the folder that contains the `.deb`. Compute its fingerprint:

```bash
sha256sum simple-astrology-app_*_amd64.deb
```

The command prints the fingerprint, two spaces, then the file name. The fingerprint must match the SHA-256 under the Debian download button.

You can also pass the file name without a wildcard:

```bash
sha256sum simple-astrology-app_0.0.1_amd64.deb
```

To let the tool do the comparison, put the checksum from the page and the file name on one line. Two spaces go between them. The file name is the file in the current directory. The command prints `OK` when they match and `FAILED` when they do not. Replace the sample hash and version with the ones on the page and the file you downloaded:

```bash
echo "paste-the-sha256-from-under-the-button  simple-astrology-app_0.0.1_amd64.deb" | sha256sum -c -
```

Install the package only after the fingerprint matches.

## Windows

Open PowerShell in the folder that contains the setup program. The file name contains spaces, so keep the quotes:

```powershell
Get-FileHash ".\Simple Astrology App Setup 0.0.1.exe" -Algorithm SHA256
```

Change `0.0.1` to the version you downloaded. The `Hash` line is the fingerprint. PowerShell prints it in uppercase. That is the same value as the lowercase checksum under the Windows download button.

Command Prompt can compute the same fingerprint with `certutil`:

```bat
certutil -hashfile "Simple Astrology App Setup 0.0.1.exe" SHA256
```

The fingerprint is the middle line. `certutil` may insert spaces between bytes. Ignore those spaces when you compare it with the checksum on the page.

Run the setup program only after the fingerprint matches.

## When the values differ

Do not install the file. Download it again from the Download section and compute the fingerprint a second time. Hash the file you are about to install. An older copy in another folder produces a different fingerprint and looks like a failed check.

If the new download still does not match the checksum under that download button, stop. Something is wrong with the file you received or with the page you copied the checksum from.

A matching checksum means the file is the one described by the value under the download button.