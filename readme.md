﻿# Pouet/ftp.scene.org database parser/mapper

A Python script designed to make the Pouet.net database more readable and create direct links to a local backup of the files originaly hosted on `ftp.scene.org`.

![Pouet Hero image](img/pouet_hero.png)

## Project Goal

The goal of this project is to parse the Pouet.net database dumps, classify productions (prods) by platform, and map their download links from `ftp.scene.org` to a local backup. This (should) allow easier exploration and access to demoscene productions offline.

### What is this all about?

- The demoscene is an international computer art subculture focused on creating demos — small, self-contained audiovisual programs that showcase technical and artistic skills. These productions often push the limits of hardware capabilities and demonstrate creative coding and design.
 - [Pouet.net](https://www.pouet.net) is the central online hub for the demoscene community. It serves as a database of demoscene productions, providing metadata, download links, and community feedback like comments and votes for each production. Pouet itself _DOES NOT HOST_ demoscene productions.
 - [Scene.org](https://scene.org) is a non-profit organization dedicated to archiving demoscene content. The `ftp.scene.org` server hosts a vast collection of demos, tools, and resources, making it a cornerstone for preserving the history of the demoscene.

### How the Script Works

1. **Fetch Data**: Downloads the latest Pouet.net database dump.
2. **Parse and Classify**: Processes the dump, organizing productions by platform and checking for download links.
3. **Remap Links**: Maps download links from `ftp.scene.org` to a local backup location.
4. **Save Results**: Saves classified productions into JSON files for easy access.
