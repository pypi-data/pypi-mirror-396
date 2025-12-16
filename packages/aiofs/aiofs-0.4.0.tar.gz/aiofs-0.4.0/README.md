# Python Anyncronous File System

There are a broad variety of data sources in the current software: sql databases, files, no-sql databases, cloud storages, ... and every one has its own methods and ways to accesing the data.

A good software architecture should not be have a strong dependency to these concrete methods and this is the purpose of this library: *Abstract the acccess to data sources from a software application*

There already are som libraries for this purpose in python (like `filesystem` ) but it is not fully oriented to asyncronous programming. It has taken as reference the library `aiofiles` as pattern to define the system
## Usage

There are only two basic classes which wrapp any data source:
1. `FileLike`, which is an object with basic file methods:
   1. Binary `read` method to access to data bytes of the file.
   2. Asyncronous binary `write` method for writing bytes to the file.
   3. Context management: `read` and `write` shall be ran within a context for assuring the proper closing and handling of file inside filesystem.
2. `FileLikeSystem`, which is a file system for the files. They have the following methods:
   1. `open` is the main method because it is the way to create and access to `FileLike` object. It is very important to have clear the future handling of the file:
      1. If the file will be used to only read, the `mode` should be `r`. This the default mode.
      2. If the file exist and will be written, the `mode` should be `r+` if you will have a reading + writing process or `w` if it only will be written.
  2. `rm` to remove one or some files
  3. `ls` to list the filenames accesibles in the file system.

There are the following possible exception:
- `BlockingIOError` if two clients are writing at the same time
- `FileNotFound` if the file does not exist in the file system

## Installation

Depending of what data source will be used, it is necessary to define extras:
1. If you are using a Operating File System it is not necessary any extras
2. If you are using Redis Data System, you'll need to add `redis` extra. The directory structure will be stored within the name of the variable. Ex. `directory/path/filename.bin` will be mapped as `directory:path:filename.bin`.
3. If you are using Azure blobs, you will need to add extra `azure`. The directory structure will go directly to the blob name. The file system is mapped to an unique blob container.

An example of manual installation for azure environment could be: `pip install aiofs[azure]`

## TODOS
 - [ ] It is intended to access to random access to files.
 - [ ] Amplify the file system methods to a better file handling
 - [ ] Add new data sources
