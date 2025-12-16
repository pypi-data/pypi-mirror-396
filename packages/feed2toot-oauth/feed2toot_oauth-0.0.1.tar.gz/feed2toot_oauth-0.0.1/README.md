### Feed2toot-oauth

Feed2toot automatically parses rss feeds, identifies new posts and posts them on the [Mastodon](https://mastodon.social) social network. It also works with gotosocial and presumably any other mastodon-like.

For the full documentation, clone and read locally under docs/source.

If you like Feed2toot, you can tip to support the development on ko-fi - no signup required:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/F2F21OVNKF)


### Quick Install

* Install Feed2toot from PyPI (recommended for normal use)

        $ python -m venv .venv
        $ source .venv/bin/activate  # Windows: .venv\Scripts\activate
        (.venv) $ pip install feed2toot-oauth

* Install Feed2toot from sources for development or local edits
  *(see the installation guide for full details
  [Installation Guide](http://feed2toot.readthedocs.io/en/latest/install.html))*

        $ git clone https://github.com/theelous3/feed2toot-oauth.git
        $ cd feed2toot-oauth
        $ python -m venv .venv
        $ source .venv/bin/activate  # Windows: .venv\Scripts\activate
        (.venv) $ pip install -e .

  Editable installs expose the same CLI commands as a normal install: `feed2toot` and `feed2toot-register-app`.


### Create the authorization for the Feed2toot app

* Run the packaged registration helper (OAuth code flow)::

        $ feed2toot-register-app
        Instance URL (e.g. https://social.example.org): https://example.social
        Open this URL in a browser, log in, and authorize the app:
        https://example.social/oauth/authorize?...
        Paste the code shown by the instance here: ABCDEFG123456
        User credentials written to ./creds/feed2toot_usercred.secret

### Use Feed2toot

* Create or modify feed2toot.ini file in order to configure feed2toot:

        [mastodon]
        instance_url=https://mastodon.social
        user_credentials=feed2toot_usercred.secret
        client_credentials=feed2toot_clientcred.secret
        ; Default visibility is public, but you can override it:
        ; toot_visibility=unlisted

        [cache]
        cachefile=cache.db

        [rss]
        uri=https://www.journalduhacker.net/rss
        toot={title} {link}

        [hashtaglist]
        several_words_hashtags_list=hashtags.txt

* Launch Feed2toot

        $ feed2toot -c /path/to/feed2toot.ini

### Authors

* Mark Jameson/theelous3 <theelous3.net>

past:

* Carl Chenet <carl.chenet@ohmytux.com>
* Antoine Beaupré <anarcat@debian.org>
* First developed by Todd Eddy


This is a big ass fork and refactor of this project, which is abandoned and very broken: https://gitlab.com/chaica/feed2toot
