# Async Course

Note that this app is designed to be administered by a teacher who is comfortable with
the Django backend. The administrative UI is not fully-developed.

## Feature Overview

- Users are put into groups
- Users have roles

This package implements an asynchronous course. The main features 
motivating this:
- A Hacker News-style threaded, weighted discussion forum.
- 

## Layout

/schedule
Shows the week-by-week curriculum, including weekly descriptions, 

/bibliography
Shows a list of references

/bibliography/PUB
Shows a publication along with 

/USER
  - Shows a user's profile

/USER/

/USER/assignments
Shows status of all assignments.

/USER/assignments/

/USER/BIBLIOGRAPHY
- Shows a user's contributed references (editable)

## Progress notes

I'm going to move away from the custom field implementation. Instead, I'm going to
write a model mixin which:

- Adds a before-save signal to compile the markdown, populate the HTML field, 
  and the error field if necessary.
- Adds a backref to publications.



