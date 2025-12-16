# Paper Inbox

<p align="left" width="250">
    <a href="https://github.com/pixelprotest/paper-inbox/actions">
        <img src="https://github.com/pixelprotest/paper-inbox/actions/workflows/tests.yml/badge.svg" alt="Tests Status">
    </a>
    <a href="">
        <img src="https://img.shields.io/github/v/release/pixelprotest/paper-inbox">
    </a>
    <a href="">
        <img src="https://img.shields.io/badge/python-3.10%20--%203.14-blue">
    </a>
    <a href="https://github.com/pixelprotest/paper-inbox/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/license-MIT-blue?style=flat">
    </a>
</p>
Overwhelmed with emails and newsletters? Lift the signal from the noise by automatically printing out email paper copies from the senders you do care about.

## What It Does
- Checks your inbox for messages from specific senders (e.g. school)
- Downloads and prints them with their attachments
- Keeps track of printed emails to avoid duplicates.
- Sends you a telegram msg whenever it prints a new email (optionally)

## Limitations
At the moment `paper-inbox` only supports authentication of `gmail` inboxes. 

## Prerequisites
Please set up a google app in your google dashboard with a Gmail API, it will provide you with a secrets file that we will use during the configuration step of `paper-inbox`

The config will run all the checks on your system and will guide you through how to install some in case they are missing. The system dependencies the app currently relies on are:
-   **libreoffice**: To turn emails into printable PDFs.
-   **CUPS**: The printing system for Linux and macOS.

## 📦 Installation
```
pip install paper-inbox
```

Then run the interactive configuration with the `--config` flag

<img alt="Config Demo" width="100%" style="border-radius:20px;" src="https://raw.githubusercontent.com/pixelprotest/paper-inbox/main/.github/demo.gif">


## 🚀 Usage
The interactive configuration should have helped you set up the app on a cron schedule, however you can also just run it manually to check everything is working:
```bash
paper-inbox
```

To see a print out of the current configuration
```
paper-inbox --show-config
```

To see a print out of the current cron schedule
```
paper-inbox --show-cron
```

To see a print out of used the directories and files
```
paper-inbox --show-dirs
```

To open the config dir:
```
paper-inbox --open-config
```

## License

MIT License. This project is for personal use.