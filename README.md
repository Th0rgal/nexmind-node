<h1 align="center">
  <br>
  <img src="https://nexmind.space/vector_logo.svg" alt="Nexmind" width="256">
  <br>
</h1>

<h4 align="center">📚 Your private search engine, dedicated to 𝘆𝗼𝘂𝗿 knowledge</h4>

<p align="center">
  <a href="https://nexmind.space"><img src="https://img.shields.io/website?down_color=lightgrey&down_message=offline&style=flat-square&up_color=green&up_message=online&url=https%3A%2F%2Fnexmind.space%2F" alt="website"></a>
  <a href="https://github.com/nexmind-space/nexmind-client"><img src="https://img.shields.io/website?label=backend&style=flat-square&up_color=blue&up_message=nexmind-client&url=https%3A%2F%2Fgithub.com%2Fnexmind-space%2Fnexmind-client"></a>
</p>

## What is nexmind for?
Have you ever searched a file for hours to never find it? Have you ever googled something like a quotation from an author you know, about a theme you know ...but which you were unable to find despite a long search?
We've been through this, and like you we hated it, so we looked for a solution but nothing satisfied us, that's why we decided to work on nexmind.

## How does it work?
Imagine a search engine that is able to search through all the data you have come across: a kind of file manager adapted to humans, not machines. To add a file you would just have to drag and drop it, specifying which spaces it belongs to and press enter. A space is a bit like a folder except that different folders can then contain the same file.
So now with nexmind if you're looking for the powerpoint of your math presentation, well you won't have to search in your lessons folder then math folder to finally realize after 10 minutes that you've left it in your documents folder: you haven't finished typing "powerpoint math presentation" that nexmind found it!

## I meant how does it **really** work?
When you add a file to nexmind, the file is hashed in a unique identifier called the "hash". The file is moved inside nexmind storage and renamed with its all new identifier. The spaces you defined are then registered to a database and associated with that hash. When you type a space list, a query is performed in order to find the corresponding files.
