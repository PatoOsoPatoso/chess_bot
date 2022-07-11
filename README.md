<!-- Intro -->
# **CHESS_BOT**
> **Lucas Arroyo Blanco**  
> 
> _PatoOsoPatoso_  

&nbsp;

<!-- Index -->
# Table of contents
## &nbsp;&nbsp;&nbsp;&nbsp;1&nbsp;)&nbsp;&nbsp;[Description](#description)
## &nbsp;&nbsp;&nbsp;&nbsp;1&nbsp;)&nbsp;&nbsp;[Requeriments](#requeriments)
## &nbsp;&nbsp;&nbsp;&nbsp;2&nbsp;)&nbsp;&nbsp;[Modifications to be used](#modifications-to-be-used) 

&nbsp;  
&nbsp; 

<!-- Description -->
## **Description**

Just a chess move indicator for [https://www.chess.com](https://www.chess.com)

***VERY IMPORTANT***

***To be able to read the state of the board you need to go to [https://www.chess.com/settings/board](https://www.chess.com/settings/board) and set Piece Notation to Text***

Is based on a tkinter window with buttons to start, stop and exit the program.

* When the Start button is pressed an automated google chrome window is opened using threading.
* If you press the Stop button that window will close.
* To exit the program press the Exit program, the driver will close and after that the program will close.
  
I recomend to use the Exit button to close the program instead of the usual X button since we are working with threads.

The arrows displayed on the tkinter window are ranked from better to worse with this colors: ***GREEN > BLUE > RED***

&nbsp;

<!-- Requeriments -->
## **Requeriments**

First of all install all the modules from [requirements.txt](requirements.txt)

On the other hand:

* Cairo on Windows
* Stockfish for your OS

&nbsp;   

<!-- Modifications -->
## **Modifications to be used**

On Windows:
* You need to install **cairo**, for that purpose I recomend to download **_uniconvertor-2.0rc5-win64_headless.msi_** from [https://sk1project.net/uc2/download/](https://sk1project.net/uc2/download/). When the file is downloaded, install it, then find the dll folder created, by default is on **_C:\Program Files\UniConvertor-2.0rc5\dlls_**. From now on you can do two things:
  
  * Add that path to your system path with the enviroment variables and remove 
  
    ```python
    os.environ['path'] += r';C:\Program Files\UniConvertor-2.0rc5\dlls'
    ```
    Or
  * Keep everything as it is and execute the program without any modificarion.

Now you need to download stockfish for your OS from [https://stockfishchess.org/download/](https://stockfishchess.org/download/). Then change the name to **stockfish**, without any extension, and place it into the project directory. 
&nbsp;  
&nbsp;

<!-- Bye bye -->
<img src="https://static.wikia.nocookie.net/horadeaventura/images/c/c2/CaracolRJS.png/revision/latest?cb=20140518032802&path-prefix=es" alt="drawing" style="width:100px;"/>**_bye bye_**