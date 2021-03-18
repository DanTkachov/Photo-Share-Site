# CS460 Programming Assignment 1 - Photosharing App

## By Daniel Bastidas and Daniel Tkachov

## Prerequesites

- Run the command ``pip3 install -r requirements.txt`` if that doesn't work try ``pip install -r requirements.txt`` to install using python3

- create a ``.env`` file and place it in the top-level folder. I have included a template that you need to fill in using your mysql username and password.

## How to Run

- To run the file you can do either ``python3 -m flask run`` while the terminal is in the top-level folder or do ``python3 app.py``.

## Notes

- I'm pretty much working fully blind on this so expect mistakes all over the place in terms of scoping and not following correct programming patterns. Fuck it really, at this point let's just get a functioning app working lol.

- Flask is the framework we're using, if you haven't used a web framework before like it before read up a little on how it works and how it integrates into python.

- There is a tutorials file that has a list of the tutorials I'm following for specific features.

- The ``_formhelpers.html`` is completely foreign to me. I copied it from a tutorial, please don't touch it cause I don't know how it works and I'm afraid of breaking it.

- Please be super careful if you make any changes to the database schema. One small change could fuck everything up and I don't understand sql enough to debug it quickly.

- Apart from that, go wild and lets make a photosharing app


## TODO

- Friends
  - ~~Adding Friends~~
  - ~~Listing Friends~~
- Albums
  - ~~User's should be able to create an album and add photos to it~~
  - ~~If a non-empty album is deleted, the photos should also be purged (probably cascade delete in the sql schema)~~
- Tags
  - ~~You should be able to tag photos~~
  - ~~If a tag doesn't exist it should be made~~
  - ~~You should be able to view all photos that belong to a tag~~
  - ~~You should be able to view the most popular tags~~
  - ~~You should be able to search for photos based on tags~~
- Comments
  - All users, registered and non-registered should be able to leave comments on photos
  - Comments should be searchable by user or comment text
- Reccomendations
  - ~~We should reccomend friends to users based on who they are friends with (friend of a friend approach)~~
  - We should reccomend other photos that a user might like based on what they have posted and tagged
