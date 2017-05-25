
# askmate-rushbit - DEVELOPER NOTES

## show_question_page function:
- question.html requires the following to be passed in when rendering:
    + question comments
    + comments for each answers

## EACH COMMENT needs:
- message body
- Edit button
- Delete button (bin icon)
- submission_time
- edited_count shown (integer, inited as 0)
    + when edited: new message AND new submission_time

## question.html changes needed:
- add comment to question button
- add comment to answer button (at each answer)
- div block for question comments
- div blocks for answer comments (at each answer)
- OBVIOUSLY: these comment blocks will be shown only if at least 1 comment is there

## show_question_list function:
- break it down into 2 pieces:
    + '/' - main page with LIMIT 5 (this should get a separate function called show_5_questions)
        + display LATEST questions!!!
    + '/list/' list page with no LIMIT (this should keep the name show_question_list)

## list.html changes needed:
- Button option to switch between 'LIMIT 5' and 'FULL LIST' versions back and forth


## SEARCH ENGINE

### Navbar - layout.html
- search field + button
- menu:
    + Home
    + Questions
    + Trending
    + Contact

### search.html
- ...

## index.html
- title h1
- div block about project:
    + title h2
    + desc about project
    + funny img
    + button link