# BadgeGenerator

Generate badges

## Setup

### Common

  1. Clone this repository somewhere on your filesystem, location really doesn't matter, but nowhere that is exposed by a web server (for production)
  2. Create a config file named "config-<env>.json" (where <env> is the environment, "dev" or "prod") in one of the following locations:
    * /etc/badgegenerator/
    * ~/.config/badgegenerator/
    * ./config/
  3. Edit the config file to override settings (defaults are in ./config/config-base.json), the bare minimum is:
    * Set DEBUG to true in dev, default is false
    * Set a real random SECRET_KEY
    * Set SQLALCHEMY_DATABASE_URI to point to your database - mysql+pymysql://<username>:<password>@<hostname>/<dbname>
    * Set UPLOAD_PATH to a directory that the application will have permission to write to
  4. Create a virtual environment (virtualenv -p python3 <location>)
  5. Install packages: /path/to/virtualenv/bin/pip install -r requirements/<env>.txt (where <env> is your environment)
  6. Set up the database: /path/to/virtualenv/bin/python manage.py db upgrade
  7. Add your user: /path/to/virtualenv/bin/python manage.py user -a <username> --ask-password
    * Note that all users are added this way regardless of environment, this command can be used to modify them too, try --help

### Development

You can run a development server on port 8000: /path/to/virtualenv/bin/python manage.py runserver (try --help for more options).
The default environment is dev, there is no need to specify it.  Do not use the development server for production.

### Production

Use a WSGI-capable server (like uWSGI), ensure it's set up to run python3 applications, and point it at wsgi.py.  The default
environment in this case is prod, there is no need to specify it.

## Usage

The interface is fairly self-explanatory, but a brief description of the components:

### Index/Home

The main page has two sections - badge templates, and the queue.

On the left, all badge templates are listed (nested to show their hierarchy) and you have the option to print many copies
of the same template (for example, badge backs or temporary badges).

On the right, the queue is shown.  The queue is the list of badges that are ready to be printed - you may add all badges
or only unprinted badges to the queue in bulk, and you can clear the queue, remove individual badges, or print them.

### Badge List

The badge list shows all badges in the system (no pagination!).  From here, all of the information about a badge is visible,
and individual badges may be added to/removed from the queue.

### Badge Upload

You can upload a CSV of badge data here.  If you paste data into the text input it must be in TSV format, otherwise an uploaded
file may be in Excel-compatible CSV format.  The fields and their meanings are listed as well.

### Administration

There are several sections in the administration interface corresponding to the different datatypes.

#### User

Users are listed here, and though they can technically be created, use the command described above to add new users or to
modify existing users.

#### Flag

Flags are bits of information about badges that are not the name, age, or level.  Examples of flag usage are to denote a
badge that is a GOH, vendor, team member, etc.  Flags are not placed on the badge, but are used to determine what template
is assigned to a given badge.  The flag names must EXACTLY match the names of flags in the external registration system or
uploaded CSV.

#### Level

The level is the type of badge, like Attendee or Sponsor.  The levels may be printed on the badge, and the names must
EXACTLY match the level names from the external registration system or uploaded CSV.

#### BadgeTemplate

Badge templates are what are rendered into the final badges.  Badge templates may inherit from other badge templates (note
that targeting information, like min/max age, and assigned levels/flags are not inherited).  Things to note:

  * The image is printed at 4" by 3" and must be this aspect ratio regardless of pixel size
  * Targeting fields (age, levels, flags) left blank match any badge
  * The template with the most matching properties is selected, though there is some weighting applied to types of matches

#### Badge

Individual badges may be created here, if necessary.