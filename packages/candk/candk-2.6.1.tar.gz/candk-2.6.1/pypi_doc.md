#  Overview

----------------------------------------


 _Corndog with Ketchup_ is a combination of tools that allows quick and simple creation of source code documentation.

##  Corndog


 A plain text extraction tool. _Corndog_ uses a special "corndog" marker ( ```-==```) in text and source code files to extract sections of text and output them to a console or file.


 _Corndog_ can parse the following file formats:

| Type | File Extension | Type | File Extension |
|---|---|---|---|
| Plain text | ```.txt``` | HTML | ```.html``` |
| Python | ```.py``` | CSS | ```.css``` |
| Java | ```.java``` | PHP | ```.php``` |
| SQL | ```.sql``` | JavaScript | ```.js``` |
| C/C++ | ```.c```/ ```.cpp``` | TypeScript | ```.ts``` |
| TaskBuilder **(deprecated)** | ```.tas``` | Vue.js | ```.vue``` |
| Properties | ```.properties``` | FreeMarker | ```.ftl``` |
| Ketchup | ```.kp``` | Bash shell script | ```.sh``` |
| XML | ```.xml``` | Windows Batch file | ```.bat``` |
| YAML | ```.yaml```/ ```.yml``` | Windows INI file | ```.ini``` |
| TOML | ```.toml``` | Conf file | ```.conf``` |


**NOTE:**  Support for TaskBuilder files ( ```.tas```) is deprecated and will be removed in a future version.



 **Usage**


 To capture text from a file, place a "corndog" marker ( ```-==```) in front of the text you wish to capture. Corndog will capture all text after the ```-==```symbol until it hits a newline or another ```-==```symbol.


 To preserve leading whitespace, use a double forward slash ( ```//```) in front of the whitespace you want to keep. By default, _Corndog_ will remove all leading whitespace.


 _Corndog_ can be run from a command line with the following command:

```
corndog -hfrm -s <start_point> -n <output_name> -x <output_extension> -o <output_directory>

```


| Option | Description |
|---|---|
| ```-h``` | Display the help text. |
| ```-f``` | Output to a single file. Use with the ```-n```and ```-x```options to set a name and file extension for the output file. |
| ```-r``` | Recursive search. If the ```start_point```provided by the ```-s```option is a directory, a recursive search will also search each subdirectory. |
| ```-X``` | Exclude files based on a file glob pattern. Can be used multiple times to exclude multiple patterns. |
| ```-m``` | Output to multiple files, with each file corresponding to a source file. The files are named the same as the source file with the subfolders prepended by hyphens (-) and the extension ```.txt```. The names cannot be set with the ```-n```option, but the extension can be changed with the ```-x```option. |
| ```-s``` | The starting point of the search. If the ```start_point```provided is a file, _Corndog_ will only parse that single file. If the ```strat_point```is a directory, it will parse every file in the directory. Use with the ```-r```option to make the search recursive. |
| ```-n``` | The name of the resulting parsed file. This option is only relevant if the ```-f```option is used. |
| ```-x``` | The file extension for the resulting file(s). This option is only relevant if the ```-f```or ```-m```option is used. |
| ```-o``` | The directory to place the resulting output file(s). This option is only relevant if the ```-f```or ```-m```option is used. |
| ```-v``` | Send warnings and errors to stderr to give more detailed feedback of the parsing and rendering. Use multiple v's to set the verbosity level ( ```-v```, ```-vv```, or ```-vvv```). |


##  Ketchup


 A special markup language designed for documenting code. It includes many specialized tags, as well as some wiki-like markup.


 _Ketchup_ can read any text-based file, but the convention is to use the ```.kp```file extension for files that contain Ketchup tags.


 **Usage**


 _Ketchup_ can be run from a command line with the following command:

```
ketchup  <filepath> -hmNw -p <page_name> -n <output_name> -o <output_directory> -c <css_file>

```


| Option | Description |
|---|---|
| ```-h``` | Display the help text. |
| ```-p``` | The name of the rendered HTML page. If the name has periods, the page title will be only the right-most portion, but the full ```.page_name```will display on the HTML page itself. |
| ```-n``` | The name of the rendered HTML file. |
| ```-o``` | The directory to place the rendered HTML file. |
| ```-c``` | Replaces the default CSS with the stylesheet specified. |
| ```-N``` | Makes h1 headers in navigation collapsible; for exceptionally large documents. |
| ```-b``` | Disable creating headers from empty newlines |
| ```-m```  ```-M``` | Export to Markdown ( ```.md```) rather than HTML ( ```.html```) |
| ```-w``` | Automatically run Ketchup rendering whenever changes are detected in the file. |
| ```-v``` | Send warnings and errors to stderr to give more detailed feedback of the parsing and rendering. Use multiple v's to set the verbosity level ( ```-v```, ```-vv```, or ```-vvv```). |


#  Using Corndog with Ketchup

----------------------------------------





 You can use _Corndog_ with _Ketchup_ with the following command

```
candk -hfrmN -s <start_point> -n <output_name> -o <output_directory> -c <css_file>

```


**NOTE:**  This command gives you file options for the _Corndog_ parsing, but it does not give you any file options for _Ketchup_. It will do its file naming and titling based on the name of the source files.


| Option | Description |
|---|---|
| ```-h``` | Display the help text. |
| ```-f``` | Output to a single file. Use with the ```-n```and ```-x```options to set a name and file extension for the output file. |
| ```-r``` | Recursive search. If the ```start_point```provided by the ```-s```option is a directory, a recursive search will also search each subdirectory. |
| ```-X``` | Exclude files based on a file glob pattern. Can be used multiple times to exclude multiple patterns. |
| ```-m``` | Output to multiple files, with each file corresponding to a source file. The files are named the same as the source file with the subfolders prepended by hyphens (-) and the extension ```.txt```. The names cannot be set with the ```-n```option, but the extension can be changed with the ```-x```option. |
| ```-s``` | The starting point of the search. If the ```start_point```provided is a file, _Corndog_ will only parse that single file. If the ```strat_point```is a directory, it will parse every file in the directory. Use with the ```-r```option to make the search recursive. |
| ```-n``` | The name of the resulting parsed file. This option is only relevant if the ```-f```option is used. |
| ```-x``` | The file extension for the resulting file(s). This option is only relevant if the ```-f```or ```-m```option is used. |
| ```-o``` | The directory to place the resulting output file(s). This option is only relevant if the ```-f```or ```-m```option is used. |
| ```-M``` | Export to Markdown ( ```.md```) rather than HTML ( ```.html```) |
| ```-c``` | Replaces the default CSS with the stylesheet specified. |
| ```-N``` | Makes h1 headers in navigation collapsible; for exceptionally large documents. |
| ```-b``` | Disable creating headers from empty newlines |
| ```-p``` | The name of the rendered HTML page. If the name has periods, the page title will be only the right-most portion, but the full ```.page_name```will display on the HTML page itself. |
| ```-v``` | Send warnings and errors to stderr to give more detailed feedback of the parsing and rendering. Use multiple v's to set the verbosity level ( ```-v```, ```-vv```, or ```-vvv```). |


#  Ketchup Markup Guide

----------------------------------------


 _Ketchup_ can read any text-based file, but the convention is to use the ```.kp```file extension for files that contain Ketchup tags.


 _Ketchup_ generally reads a file top-to-bottom, and splits the file into sections. A new section is marked by an empty line or a **tag**, which always starts with an "at" symbol ( ```@```). _Ketchup_ does not preserve whitespace (multiple spaces, newlines, and tabs) unless a tag is specifically made to do so. There are 3 types of markup in _Ketchup_: **inline**, **frontline**, and **tags**.


 One key difference from other markup languages is that Ketchup tags **cannot** be nested. You cannot put a ```@table```tag inside a ```@return```tag. You can, however, nest inline markup inside other inline markup or in frontline markup as well as certain tags.

##  Inline Markup


 _Inline markup_ is markup that can occur anywhere in a line of text, _even within some tags_.

#### ``` \ (backslash)```


 The backslash will let you escape any character that would normally be used by _Ketchup_ for inline or frontline markup.


 **Markup:**

```
Email: charles\@cerrax.com

```






 **Render:**


 Email: charles@cerrax.com

#### ``` @ (line break)```


 The line break lets you insert a newline in a tag that normally wouldn't let you have one.


 **Markup:**

```
I like this place@
@
But I don't@
want to
be here anymore.@
Good-bye!

```






 **Render:**


 I like this place<br /> <br /> But I don't<br /> want to be here anymore.<br /> Good-bye!

#### ``` / (code)```


 Very often when documenting source code, you'll want to reference a variable name or a method. To make these references stand out and avoid confusion when the name is a very common word, use the forward slash (known as the code markup) to mak the word directly following it styled in a monospace font that is similar to how most IDE's display source code.

**NOTE:**  Other inline markups (bold, italic, codeline, and line break) will not be applied to the word styled by this markup.



 **Markup:**

```
When testing this method, set the /startTime value to 0 for best results.

```






 **Render:**


 When testing this method, set the ```startTime```value to 0 for best results.

#### ``` /- -/ (codeline)```


 When documenting code, it may be useful to provide short snippets of code. Whereas the forward slash provides a single word with the appropriate styling, the codeline markup provides a way to mark a whole string as a code segment.

**NOTE:**  Other inline markups (bold, italic, code, and line break) will not be applied to the word styled by this markup.



 **Markup:**

```
The function will exit the loop prematurely if /-num_parkas/1.2 <= 3-/ and you initialize the rainstorm.

```






 **Render:**


 The function will exit the loop prematurely if ```num_parkas/1.2 <= 3``` and you initialize the rainstorm.

#### ``` ! (hyperlink)```


 When you need to provide a link, use an exclamation mark (!) at teh bgeinning of the link to make it clickable.

**NOTE:**  Other inline markups (bold, italic, code/codeline, and line break) will not be applied to the word styled by this markup.



 **Markup:**

```
Follow the yellow brick road: !http://www.cerrax.com

```






 **Render:**


 Follow the yellow brick road: [http://www.cerrax.comhttp://www.cerrax.com](http://www.cerrax.com)

#### ``` *bold*```


 To mark a string as bolded style, place asterisks on either side. Make sure there isn't any space between the asterisk and the first character, or the styling will not take effect.


 **Markup:**

```
"You don't understand!" he cried, "You *really* won't like me when I'm angry..."

```






 **Render:**


 "You don't understand!" he cried, "You **really** won't like me when I'm angry..."

#### ``` _italics_```


 To mark a string as italic style, place a single underscore on either side. Make sure there isn't any space between the underscore and the first character, or the styling will not take effect.


 **Markup:**

```
"Miss, don't be alarmed, but the call is coming _from inside the house._" the police officer said.

```






 **Render:**


 "Miss, don't be alarmed, but the call is coming _from inside the house._" the police officer said.




##  Frontline Markup


 _Frontline markup_ is markup that only applies if it is the first mark on a line. Frontline markup can contain inline markup, but it cannot contain tags or other frontline markup.

#### ``` - (unbulleted list)```


 To make a list that has no bullet points next to the list items, place hyphens with a space after to create a list. The more hyphens you add, the deeper the list (to a maximum of 4).


 **Markup:**

```
- This is a list
- *It has items* in it. Some items
    Are more fun than others
    But it's all in good fun.
-- This is a _deeper list_
--- Even /deeper still. Pretty neat huh?
    It is a marvelous world
- Now /-we're back to the first-/ level
--- And we can jump to the third!

```






 **Render:**

- This is a list
- **It has items** in it. Some items Are more fun than others But it's all in good fun.
  - This is a _deeper list_
    - Even ```deeper```still. Pretty neat huh? It is a marvelous world
- Now ```we're back to the first``` level
    - And we can jump to the third!


#### ``` * (bulleted list)```


 To make a list with bullet points, place asterisks with a space after to create a list. The more asterisks you add, the deeper the list (to a maximum of 4).


 **Markup:**

```
* This is a bulleted list!
** See how deep it gets!
*** Yowza!
**** Level four

```






 **Render:**

* This is a bulleted list!
  * See how deep it gets!
    * Yowza!
      * Level four


#### ``` # (numbered list)```


 To make an ordered list, place hash marks with a space after to create a list. The more hash marks you add, the deeper the list (to a maximum of 4).


 **Markup:**

```
# Numbered list
# See it counting up?
## Second level
### How deep does
    the rabbot hole go?
#### Pretty deep actually
## Wow
# Pretty cool

```






 **Render:**

1 Numbered list
1 See it counting up?
  1 Second level
    1 How deep does the rabbot hole go?
      1 Pretty deep actually
  1 Wow
1 Pretty cool





##  Tags


 Every tag in _Ketchup_ is marked with an "at" symbol ( ```@```). Tags must be on their own line. Each line after the tag is considered part of that tag. Once an empty line  or another tag is encountered, the tag will close.

**NOTE:**  _Ketchup_ cannot nest tags and tags cannot contain frontline markup. However, tags can contain inline markup.


#### ``` @page```


 By default, _Ketchup_ uses the source filepath as the page name. The filename is used for the HTML ```<title>```tag and the full filepath is the title displayed on the page.


 **Markup:**

```
@page
directory.another_dir.module

```






 **Render:**


 The page will render with _**module**_ as the name displayed in the tab of the browser and _**directory.another_dir.module**_ in the black title bar across the top of the page. This is a **single-line tag**, meaning that multiple lines will be concatenated into a single line.

#### ``` @file```


 Defines the filename that this document should have.

**NOTE:**  Only valid file names will work. Invalid file names will cause _Ketchup_ to throw an exception.



 **Markup:**

```
@file
Output-File-name

```






 **Render:**


 This will create an HTML file named ```Output-File-name.html```

#### ``` @outdir```


 Defines the filepath to place the rendered HTML file.

**NOTE:**  It is recommended to use an absolute filepath. This is because a relative filepath with start from the ```start_point```provided to _Ketchup_ and thus the correct path cannot be guaranteed.



 Markup:

```
@outdir
/Users/user1/Documents/Ketchup-Docs

```






 **Render:**


 This will save the rendered HTML in a file at ```/Users/user1/Documents/Ketchup-Docs```.

#### ``` @byline```


 Any information that pertains to the authorship, ownership, or relationship of a section should be placed in a ```@byline```tag. This is a **multi-line tag**, meaning that each line will stay on its own line.


 **Markup:**

```
@byline
Project Awesome v1.3.76
Charlie Koch - January 25, 2016

```






 **Render:**

> * Project Awesome v1.3.76
> * Charlie Koch - January 25, 2016


#### ``` @imports```


 Any modules or other code that is needed for this code to work (e.g. Java ```import```, or C/C++ ```include```, or HTML ```<link>```or ```<script>```tags). This is a **multi-line tag**, meaning that each line will stay on its own line.


 **Markup:**

```
@imports
import os, sys
from module.another_module.file import MyClass, BetterClass
from module.different_module.file2 import Class2

```






 **Render:**

**Imports:**

* ```import os, sys```
* ```from module.another_module.file import MyClass, BetterClass```
* ```from module.different_module.file2 import Class2```


#### ``` @class```


 Marks the following line(s) as the header of a class. This is a **single-line tag**, meaning that multiple lines will be concatenated into a single line.


 This tag also creates an entry in the navigation sidebar.

**NOTE:**  Inline markups (bold, italic, code, and line break) will not be applied to text styled by this tag.



 **Markup:**

```
@class
public GreatObject extends AnotherObject
                        implements AnInterface

```






 **Render:**

<div class="class">public GreatObject extends AnotherObject implements AnInterface</div>



#### ``` @method```


 Marks the following line(s) as the header of a function or method. This is a **single-line tag**, meaning that multiple lines will be concatenated into a single line.


 This tag also creates an entry in the navigation sidebar.

**NOTE:**  Inline markups (bold, italic, code, and line break) will not be applied to text styled by this tag.



 **Markup:**

```
@method
def prepareLaunch(power, payload,
                    vector1, vector2,
                    spaceship, fuel_type)

```






 **Render:**

<div class="method">def prepareLaunch(power, payload, vector1, vector2, spaceship, fuel)</div>



#### ``` @deflist```


 Creates a table with names and their descriptions. Each line is a row of the table in the format: ```def_name: Description of the definition``` . The ```def_name```section ignores all markup. The description allows inline markup.


 The ```@attributes```, ```@params```, ```@constants```, and ```@exceptions```tags do the same formatting with special headers attached.


 **Markup:**

```
@deflist
definition: this is a definition
def2: this is another def
whoa: this is cool

@attributes
str: The string to search
chars: Number of characters to search
variable_name: Description

@constants
MAX_RETRIES: Maximum number of retries to
             attempt before quitting
TIMEOUT: Time in seconds before the communication should end
SUCCESS_STRING: The string that prints if successful

@params
start_time: Time when this function started
end_time: Time when this function should end
filepath: Where this function should place the output

@exceptions
DataAccessError: database access error
BusinessLogicError: when something violates the rules

```



 **Render:**

* ```definition```: this is a definition
* ```def2```: this is another def
* ```whoa```: this is cool


**Attributes:**

* ```str```: The string to search
* ```chars```: Number of characters to search
* ```variable_name```: Description


**Constants:**

* ```MAX_RETRIES```: Maximum number of retries to attempt before quitting
* ```TIMEOUT```: Time in seconds before the communication should end
* ```SUCCESS_STRING```: The string that prints if successful


**Parameters:**

* ```start_time```: Time when this function started
* ```end_time```: Time when this function should end
* ```filepath```: Where this function should place the output


**Exceptions:**

* ```DataAccessError```: database access error
* ```BusinessLogicError```: when something violates the rules


#### ``` @return```


 A small section that details the return value of a method or function.


 This is a **single-line tag**, meaning that multiple lines will be concatenated into a single line.


 **Markup:**

```
@return
A small integer, but not too small. But just right.
Ask Goldilocks about it...

```






 **Render:**

**Returns:**  A small integer, but not too small. But just right. Ask Goldilocks about it...


#### ``` @h1, @h2, @h3, @h4```


 Standard wiki-like header tags. The smaller the number, the larger the text.


 Header sizes 1 and 2 ( ```@h1```and ```@h2```) also create an entry in the navigation sidebar.


 Headers are a special tag which can also be used at the bgeinning of line, rather than on the line above.

**NOTE:**  Inline markups (bold, italic, code, and line break) will not be applied to text styled by this tag.



 **Markup:**

```
@h1
Header 1

@h1 Header 1

@h2
Header 2

@h2 Header 2

@h3
Header 3

@h3 Header 3

@h4
Header 4

@h4 Header 4

```






 **Render:**

#  Header 1

#  Header 1

##  Header 2

##  Header 2

###  Header 3

###  Header 3

####  Header 4

####  Header 4





 Headers 1 and 2 ( ```@h1```and ```@h2```) can also be defined by using blank lines above them. 3 blank lines makes a Header 1, and 2 blank lines makes a Header 2. You can disable this option with the ```-b```command line flag.

**NOTE:**  When using blank lines to create a header, you cannot place 1 Header tag directly beneath another. There must be some text or other tag below the header before defining the next one.


```
This is a paragraph.



Header 1

Text here.


Header 2

More text.

```






 **Render:**


 This is a paragraph.

#  Header 1


 Text here.

##  Header 2


 More text.

#### ``` @table```


 A simple table element. Because _Ketchup_ can't nest tags, you cannot use any tags inside the table. However, inline markup still works.


 Each line is a row of the table. Each column is separated by a pipe ( ```|```), **but** there are no pipes on the ends of the row. The first row is the header row. The next row is a row of at least 3 hyphens ( ```---```) to mark the end of the header. Each row after that is a simple row of the table.


 **Markup:**

```
@table
Column 1     | Column 2 | Column 3
-----------------------------------------
Data in here | more     |
             | Stuff    | _More_ data in here!
/Data?       |          | *Even more!*

```






 **Render:**

| Column 1 | Column 2 | Column 3 |
|---|---|---|
| Data in here | more |  |
|  | Stuff | _More_ data in here! |
| ```Data?``` |  | **Even more!** |


#### ``` @image```


 Embed an image in your Ketchup document.


 The image will be automatically sized, however you can adjust the image's size to your preference. Include ```height=<size>```or ```width=<size>```separated by a space or on the next line.

**NOTE:**  Markdown does not allow changing the size of the image natively. You can work around this by using a ```@literal```tag with an HTML ```<img>```element.



 **Markup:**

```
@image
https://www.python.org/static/community_logos/python-logo.png width=600px

```






 **Render:**

![](https://www.python.org/static/community_logos/python-logo.png)

#### ``` @br```


 A sort-of line break (hence the "br") that provides extra whitespace between elements.


 **Markup:**

```
Section

Another section

This is a section@with an inline break.
@br
And this a line break!

```






 **Render:**


 Section


 Another section


 This is a section<br />with an inline break.





 And this a line break!

#### ``` @hr ___```


 A horizontal rule, useful for separating sections to improve readability. An alternate markup for the horizontal rule is 3 underscores ( ```___```) though anything more than 3 will work.


 **Markup:**

```
Using the /\@hr tag
@hr
Using the /___ markup
___
Using a longer underscore markup
____________________________

```






 **Render:**


 Using the ```@hr```tag

----------------------------------------


 Using the ```___```markup

----------------------------------------


 Using a longer underscore markup

----------------------------------------

#### ``` @codeblock```


 Since the inline markup for ```code```and ```codeline```only works on a single line and doesn't preserve whitespace, this tag provides exactly than for larger sectiosn of code. Because of this, it requires a second tag at the end of the block: ```@codeblockend```.

**NOTE:**  As with all code markup, inline markups (bold, italic, code, and line break) will not be applied to text styled by this tag.



 **Markup:**

```
@codeblock
There's code in here.
    Lots of code.
        So much code!

    For real, this is crazy.
&#64;codeblockend

```






 **Render:**

```
There's code in here.
    Lots of code.
        So much code!

    For real, this is crazy.

```


#### ``` @literal```


 Similar to the codeblock, but still renders the text in regular section rather than monspace. Usually HTML will collapse all whitespace into a single space character, so keep that in mind when using this tag. It's mainly for entering large sections of text that may contain many characters and tags that are used by _Ketchup_. Can also be used to insert HTML or other markup languages in a _Ketchup_ document.


 **Markup:**

```
@literal
This is a literal
@br

There's some crazy /stuff _in this tag_
but Ketchup *won't render any of it*.
<div style="border: 1px solid black;background-color:green;width:20rem;">This is a div</div>

# List
## Numbered list
&#64;literalend

```






 **Render:**

This is a literal
@br

There's some crazy /stuff _in this tag_
but Ketchup *won't render any of it*.
<div style="border: 1px solid black;background-color:green;width:20rem;">This is a div</div>

# List
## Numbered list



#### ``` @note```


 Inserts a special note section that can used to bring a specific section to the reader's attention or add a significant footnote. The italic inline markup does appear to change the style of the text since this tag makes text italic by default.


 This is a **single-line tag**, meaning that multiple lines will be concatenated into a single line.


 **Markup:**

```
@note
You must be careful. _*Never*_ underestimate
the power of the /-Dark Side-/.

```






 **Render:**

**NOTE:**  You must be careful. _**Never**_ underestimate the power of the ```Dark Side```.


