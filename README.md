<h1>Prerequisites:</h1>
<ol>
  <li>Download Python (https://www.python.org/downloads/)</li>
  <li>Add Python and Pip (a package installer included in the above) to your PATH if on Windows (https://www.geeksforgeeks.org/python/how-to-add-python-to-windows-path/)</li>
  <li>Download this code to your machine.</li>
  <li>Open a command line/ powershell window in your downloaded folder and run the following command: "pip install -r requirements.txt" to install the needed additional packages.</li>
  <li>Run the program (using the command line/ powershell window) with "python main.py".</li>
</ol>

<h1>Main Window:</h1>
<img width="286" height="277" alt="1  main window" src="https://github.com/user-attachments/assets/5bf622bd-b2c1-4eac-a7e7-cb42a2d1604c" />
<br />
<h4>Enter IDs:</h4>
<p>Enter the IDs of the characters/ lightcones/ relicsets whose data you want. Leaving this window blank before pressing "Submit" will instead query the contents of shortlist.txt (explained later). A tooltip will explain this if you hover over the textbox.</p>
<h4>Getting updates:</h4>
<p>You can check Hakush.in for updates for characters, lightcones and relicsets by selecting/ deselecting those options with the buttons named after them. Add/ Remove All will do as described to all three. Check "Names" if you want the names of the new items included in the output (otherwise you will just get their IDs).</p>
<h4>Short & Blacklists:</h4>
<p>Opens a text editor in a separate window (see below).</p>
<h4>View saved IDs:</h4>
<p>Opens in a separate window (see below).</p>
<h4>Set Weekly (Bosses):</h4>
<p>Opens in a separate panel (see below).</p>

<h1>Shortlist/ Blacklist Window:</h1>
<img width="274" height="182" alt="2  short + blacklist" src="https://github.com/user-attachments/assets/b2ea46df-0820-4fbf-b17c-3cd106ba7476" />
<p>(Both windows have the same UI.)</p>
<h4>Shortlist:</h4>
<p>Enter the IDs of items you will be querying often here, one per line. These will be saved to shortlist.txt and used when the "Enter IDs" text field is left empty, as described above.</p>
<h4>Blacklist:</h4>
<p>Enter the IDs of characters you don't want to see the full details of. When these items are queried, a separate "(Simple)" file will also be generated, listing just their base stats, Minor Traces and needed materials.</p>

<h1>Item Lists Window:</h1>
<img width="284" height="208" alt="3  item lists" src="https://github.com/user-attachments/assets/4f8e578b-4281-4416-a311-8c5f29b3da30" />
<p>Use the tabs at the top of the window to load the character/lightcone/relicset.json files saved on your system. These files are created and updated whenever you check for updates (as described above).</p>

<h1>Set Weeklies:</h1>
<img width="286" height="322" alt="4  set weeklies panel" src="https://github.com/user-attachments/assets/40a1a1e8-7040-4b2f-bcb6-aa390bcf4ac0" />
<p>Story arcs in Honkai Star Rail are punctuated with major bosses. As the materials from these bosses can be considered spoilers, you can set which ones you've done here.</p>
<p>When fetching a character's kit, this value will be used to replace the names of unfought materials with "???". You can update this value as you play more of the game (or by manually editing the file when the app is not running).</p>
<p>Note that text here is written to "weekly bosses.txt". Editing this file manually (i.e. without using this panel) while the app is running WILL NOT WORK.</p>
<p>P.S. The default value (e.g. when running this app for the first time) is 0.</p>
