# Wiki Application For Tunes

<p align="center">
    <img height=260 width=600 src="media/pnuemy.svg">
    <br>
    <br>
    <a href="mongodb+srv://lpdh3m_db_user:wiki_app_for_tunes_pass@wiki-app-for-tunes.5juoymq.mongodb.net/">
        <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white">
    </a>
</p>

[comment]: # (Todo. Add badges, particularlly build status, test status, docs coverage and test coverage.)

`waft` is a [textual user interface](https://en.wikipedia.org/wiki/Text-based_user_interface) application that facilitates the association of files in the [MP3](https://ossrs.io/lts/zh-cn/assets/files/ISO_IEC_13818-3-MP3-1997-8bbd47f7cd4e0325f23b9473f6932fa1.pdf) format with metadata according to the [ID3 standard](https://id3.org/id3v2.3.0).
## Installation
[comment]: # (Todo. May look having user download repository or otherwise we may also opt to host the application as a website.)
Installation instructions will be published once deployment infrastructure is finalized.
## Usage
Usage instructions will be provided once the command-line interface and core workflows are finalized.
## Implementation Details
[comment]: # (Todo. This section should contain an explanation of both the Entity Relation diagram of our database written in Mermaid, as well as the implementation of the Elm design Pattern for our front end logic.)
This section will provide a detailed explanation of the database entity relationships and the application’s implementation of the Elm Architecture once design documentation is complete.
```mermaid
erDiagram
    ARTIST {
        string ID PK
        string Name
    }
    TRACK {
        string ID PK
        string Name
        date ReleaseDate
        int Duration
        boolean explicit
    }
    ALBUM {
        string ID PK
        string Name
        string CoverImageLink
    }
    FILE {
        string Hash PK
        string TrackID FK
        string SourceLink
    }
    RECORDS {
        string ArtistID FK
        string TrackID FK
    }
    ON {
        string TrackID FK
        string AlbumID FK
        int TrackNumber
    }
    ARTIST ||--o{ RECORDS : ""
    TRACK ||--|| RECORDS : ""
    TRACK o|--|| FILE : ""
    TRACK ||--|| ON : ""
    ALBUM o|--o{ ON : ""
```
TEA - https://guide.elm-lang.org/architecture/
## Contribution Guide
Check out our [Contribution Guide](CONTRIBUTING.md) for more information on how to contribute to the project.
