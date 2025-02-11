# Speaky Bird

SpeakyBird is a modified version of the famous Flappy Bird game, but with speech recognition. This version is inspired by the [SmileyBird](https://github.com/mert-o/FlappyBird) project. Unlike SmileyBird, here the game is controlled by saying the commands displayed on the screen. These commands are customizable. To recognize the voice commands [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) model is used.

## Installation (Tested on Ubuntu 22.04.4 LTS and Windows 10)
**Speech recognition works faster on Ubuntu than Windows making the game more enjoyable.**

1. Clone the repository using `git clone https://github.com/Vaish1795/SpeakyBird.git`

**!! Do not directly run the requirements file as it will not install openai whisper and faster whisper properly. Some packages in the openai whisper are not compatible with the higher version of the faster whisper resulting in conflicts. Follow the steps (Tested on Ubuntu and Windows)**

**Anaconda/Miniconda users**
-First, create a new Conda environment and activate it:
```bash
conda create --name <your environment name> python=3.10 -y
conda activate <your environment name>
```
2. Openai-whisper and Faster whisper needs to be installed separately before running the requirements file, as some of the inbuilt packages are conflicting. To do this follow the steps.
```bash
pip install "openai-whisper @ git+https://github.com/openai/whisper.git@ba3f3cd54b0e5b8ce1ab3de13e32122d0d5f98ab"
```
Next, install faster whisper:
```bash
pip install "faster-whisper @ git+https://github.com/SYSTRAN/faster-whisper.git"
```

3. Install the required packages using `pip install -r requirements.txt`

Note: *webRTC VAD package requires visual studio build tools to be installed on windows. If you encounter an error while installing webrtcvad, install visual studio build tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/. Make sure Windows 10SDK is installed and rerun the requirements file.*
4. Navigate to the `src` directory using `cd speakbird/src`
5. Run the game using `python main.py`
5. Say the commands displayed on the screen to control the bird
6. Enjoy!

## Possible Errors in Ubuntu 21 onwards and Miniconda users 

**OpenGL error in Ubuntu and miniconda users**
If you encounter the following OpenGL errors in Ubuntu while using Miniconda:

```
libGL error: MESA-LOADER: failed to open iris: /usr/lib/dri/iris_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
libGL error: failed to load driver: iris
libGL error: MESA-LOADER: failed to open iris: /usr/lib/dri/iris_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
libGL error: failed to load driver: iris
libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)
libGL error: failed to load driver: swrast
```
In the terminal first check the version of libstdc++ by running the following command:
```bash
strings /usr/lib/x86_64-linux-gnu/libstdc++.so.6 | grep GLIBCXX
```
If GLIBCXX_3.4.30 is not listed, update your system's libstdc++
```bash
sudo apt update && sudo apt install libstdc++6
```
Rerun the command to check the version of libstdc++ and if GLIBCXX_3.4.30 is listed by running the following command:
```bash
strings /usr/lib/x86_64-linux-gnu/libstdc++.so.6 | grep GLIBCXX
```
Since Miniconda comes with an older version, remove the existing one and link the system version
```
mv ~/miniconda3/envs/test/lib/libstdc++.so.6 ~/miniconda3/envs/<your environment name>/lib/libstdc++.so.6.backup
ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 ~/miniconda3/envs/<your environment name>/lib/libstdc++.so.6
```
Replace `<your environment name>` with the name of the environment you created.

For a global Miniconda fix, apply the same steps to ~/miniconda3/lib/:
```
mv ~/miniconda3/lib/libstdc++.so.6 ~/miniconda3/lib/libstdc++.so.6.backup
ln -s /usr/lib/x86_64-linux-gnu/libstdc++.so.6 ~/miniconda3/lib/libstdc++.so.6
```
Reboot your system for the changes to reflect:
```bash
sudo reboot
```
Run the game.

## Folder Structure
1. **src**: Contains the source code of the game
2. **assets**: Contains the images, fonts and sounds used in the game

## Different Modes
1. **Pipe Mode**: The bird has to pass through the pipes by saying the command.
2. **Fireball Mode**: The bird has to dodge the fireballs and shoot the negative statements by saying the command. To move up or down the screen, keyboard keys should be used.
3. **Combined Mode**: Both pipes and Fireball mode are combined with a staircase mode acting as an intermediate level. To climb the stairs, the player has to say the command displayed on the screen.

One can choose different modes in the settings menu of the game. By default Pipes mode is selected.

## Customization
To change the commands, 
1. Navigate to the `src` directory
2. Open `global_var.py` file
3. Edit the variables `command_pipe`, `command_fireball` or `command_stairs`

## Changing model for speech recognition (For german language)
1. Navigate to the `src` directory
2. Open `transcriber_faster_whisper.py` file
3. Change the model from `tiny.en` in `model` variable to `tiny` for german language.

One can view the different models available at https://github.com/openai/whisper.

## References
1. Faster-Whisper https://github.com/SYSTRAN/faster-whisper.
2. Openai Whisper https://github.com/openai/whisper.
3. SmileyBird Project https://github.com/mert-o/FlappyBird.