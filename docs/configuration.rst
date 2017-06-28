Configuration
#############

Contents
========

1) `General Options`_
2) `Output Options`_
3) `Downloader Options`_
4) `Extractor Options`_
5) `Extractor-specific Options`_


General Options
===============

base-directory
--------------
=========== =====
Type        ``string``
Default     ``"./gallery-dl/"``
Description Directory path used as the base for all download destinations.
=========== =====


netrc
-----
=========== =====
Type        ``bool``
Default     ``false``
Description Enable the use of |.netrc|_ authentication data.
=========== =====


cache.file
----------
=========== =====
Type        ``string``
Default     |tempfile.gettempdir()|_ + ``".gallery-dl.cache"``
Description Path of the SQLite3 database used to cache login sessions,
            cookies and API tokens.

            Set this value to an invalid path or simply ``null`` to disable
            this cache.
=========== =====


Output Options
==============

output.mode
-----------
=========== =====
Type        ``string``
Default     ``"auto"``
Description Controls the output string format and status indicators.

            * ``"null"``: No output
            * ``"pipe"``: Suitable for piping to other processes or files
            * ``"terminal"``: Suitable for the standard Windows console
            * ``"color"``: Suitable for terminals that understand ANSI escape codes and colors
            * ``"auto"``: Automatically choose the best suitable output mode
=========== =====


output.shorten
--------------
=========== =====
Type        ``bool``
Default     ``true``
Description Controls whether the output strings should be shortened to fit
            on one console line.
=========== =====

output.progress
---------------
=========== =====
Type        ``bool`` or ``string``
Default     ``true``
Description Controls the progress indicator when ``gallery-dl`` is run with
            multiple URLs as arguments.

            * ``true``: Show the default progress indicator
              (``"[{current}/{total}] {url}"``)
            * ``false``: Do not show any progress indicator
            * Any ``string``: Show the progress indicator using this
              as a custom `format string`_. Possible replacement keys are
              ``current``, ``total``  and ``url``.
=========== =====


Downloader Options
==================

downloader.http.retries
-----------------------
=========== =====
Type        ``integer``
Default     ``5``
Description Number of times a failed download is retried before giving up.
=========== =====


downloader.http.timeout
-----------------------
=========== =====
Type        ``float`` or ``null``
Default     ``null``
Description Amount of time (in seconds) to wait for a successful connection
            and a response from a remote server.

            This value gets internally used as the ``timeout`` parameter for the
            |requests.get()|_ method.
=========== =====


Extractor Options
=================

| Each extractor is identified by its ``category`` and ``subcategory``.
| The ``category`` is the lowercase site name without any spaces or special
  characters, which is usually just the module name
  (``pixiv``, ``batoto``, ...).
  The ``subcategory`` is a lowercase word describing the general functionality
  of that extractor (``user``, ``favorite``, ``manga``, ...).


Each one of the following options can be specified on multiple levels of the
configuration tree:

================== =====
Base level:        ``extractor.<option-name>``
Category level:    ``extractor.<category>.<option-name>``
Subcategory level: ``extractor.<category>.<subcategory>.<option-name>``
================== =====

A value in a "deeper" level hereby overrides a value of the same name on a
lower level. Setting the ``extractor.pixiv.filename`` value, for example, lets
you specify a general filename pattern for all the different pixiv extractors.
Using the ``extractor.pixiv.user.filename`` value lets you override this
general pattern specifically for ``PixivUserExtractor`` instances.

The ``category`` and ``subcategory`` of an extractor used for a specific URL
can be determined by using the ``--list-keywords`` command-line option
(see the example below).

If that does not work, the extractor names, which can be obtained from
``gallery-dl --list-extractors``, provide an alternative:
Each extractor name is structured as ``CategorySubcategoryExtractor``.
An extractor called ``PixivUserExtractor`` has therefore the category ``pixiv``
and the subcategory ``user``.

extractor.*.filename
--------------------
=========== =====
Type        ``string``
Example     ``"{manga}_c{chapter}_{page:>03}.{extension}"``
Description A `format string`_ to build the resulting filename
            for a downloaded file.

            The available replacement keys depend on the extractor used. A list
            of keys for a specific one can be acquired by calling *gallery-dl*
            with the ``--list-keywords`` command-line option.
            For example:

            .. code::

                $ gallery-dl --list-keywords http://seiga.nicovideo.jp/seiga/im5977527
                Keywords for directory names:
                -----------------------------
                category
                  seiga
                subcategory
                  image

                Keywords for filenames:
                -----------------------
                category
                  seiga
                extension
                  None
                image-id
                  5977527
                subcategory
                  image

            Note that even if the value of the ``extension`` key is missing or
            ``None``, it will filled in later when the file download is
            starting. This key is therefore always available to provide
            a valid filename extension.
=========== =====


extractor.*.directory
---------------------
=========== =====
Type        ``list`` of ``strings``
Example     ``["{category}", "{manga}", "c{chapter} - {title}"]``
Description A list of `format strings`_ for the resulting target directory.

            Each individual string in such a list represents a single path
            segment, which will be joined together and prepended with the
            base-directory_ to form the complete target directory path.
=========== =====


extractor.*.skip
----------------
=========== =====
Type        ``bool`` or ``string``
Default     ``true``
Description Controls the behavior when downloading a file whose filename
            already exists.

            * ``true``: Skip the download
            * ``false``: Overwrite the already existing file
            * ``"abort"``: Abort the current extractor run
            * ``"exit"``: Exit the program altogether
=========== =====


extractor.*.username
--------------------
=========== =====
Type        ``string``
Default     ``null``
Description The username to use when attempting to log in to another site.

            Specifying a username is required for the ``pixiv``, ``nijie`` and
            ``seiga`` modules and optional (but strongly recommended) for
            ``batoto`` and ``exhentai``.

            This value can also be given via the ``-u/--username``
            command-line option or by using a |.netrc|_ file.
            (see Authentication_)
=========== =====


extractor.*.password
--------------------
=========== =====
Type        ``string``
Default     ``null``
Description The password belonging to the username.
=========== =====


Extractor-specific Options
==========================

extractor.deviantart.mature
---------------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Enable mature content.

            This option simply sets the |mature_content|_ parameter for API
            calls to either ``"true"`` or ``"false"`` and does not do any other
            form of content filtering.
=========== =====


extractor.exhentai.original
---------------------------
=========== =====
Type        ``bool``
Default     ``true``
Description | Always download the original image or
            | download the down-sampled version for larger images.
=========== =====


extractor.exhentai.wait-min
---------------------------
=========== =====
Type        ``float``
Default     ``3.0``
Description Minimum wait time in seconds between each image

            Exhentai detects and blocks automated downloaders.
            ``gallery-dl`` waits a randomly selected number of
            seconds between ``wait-min`` and ``wait-max`` after
            each image to prevent getting blocked.
=========== =====


extractor.exhentai.wait-max
---------------------------
=========== =====
Type        ``float``
Default     ``6.0``
Description Maximum wait time in seconds
=========== =====


extractor.flickr.access-token
-----------------------------
=========== =====
Type        ``string``
Default     ``null``
Description The ``access_token`` value you get from linking your Flickr account
            to ``gallery-dl``.
=========== =====


extractor.flickr.access-token-secret
------------------------------------
=========== =====
Type        ``string``
Default     ``null``
Description The ``access_token_secret`` belonging to the ``access_token``.
=========== =====


extractor.flickr.metadata
-------------------------
=========== =====
Type        ``bool``
Default     ``false``
Description Load additional metadata when using the single-image extractor.
=========== =====


extractor.flickr.size-max
--------------------------
=========== =====
Type        ``integer`` or ``string``
Default     ``null``
Description Sets the maximum allowed size for downloaded images.

            * If this is an ``integer``, it specifies the maximum image dimension
              (width and height) in pixels.
            * If this is a ``string``, it should be one of Flickr's format specifiers
              (``"Original"``, ``"Large"``, ... or ``"o"``, ``"k"``, ``"h"``,
              ``"l"``, ...) to use these as an upper limit.
=========== =====


extractor.gfycat.format
-----------------------
=========== =====
Type        ``string``
Default     ``"mp4"``
Description The name of the preferred animation format, which can be one of
            ``"mp4"``, ``"webm"``, ``"gif"``, ``"webp"`` or ``"mjpg"``.

            If the selected format is not available, ``"mp4"``, ``"webm"``
            and ``"gif"`` (in that order) will be tried instead, until an
            available format is found.
=========== =====


extractor.imgur.mp4
-------------------
=========== =====
Type        ``bool`` or ``string``
Default     ``true``
Description Controls whether to choose the GIF or MP4 version of an animation

            * ``true``: Follow Imgur's advice and choose MP4 if the
              ``prefer_video`` flag in an image's metadata is set.
            * ``false``: Always choose GIF.
            * ``"always"``: Always choose MP4.
=========== =====


extractor.oauth.browser
-----------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Controls how a user is directed to an OAuth authorization site.

            * ``true``: Use Python's |webbrowser.open()|_ method to automatically
              open the URL in the user's browser.
            * ``false``: Ask the user to copy & paste an URL from the terminal.
=========== =====


extractor.pixiv.ugoira
----------------------
=========== =====
Type        ``bool``
Default     ``true``
Description Download Pixiv's Ugoira animations or ignore them.

            These animations come as a ``.zip`` file containing all the single
            animation frames in JPEG format.
=========== =====


extractor.reddit.comments
-------------------------
=========== =====
Type        ``integer`` or ``string``
Default     ``200``
Description The value of the ``limit`` parameter when loading
            a submission and its comments.
            This number (roughly) specifies the total amount of comments
            being retrieved with the first API call.

            Reddit's internal default and maximum values for this parameter
            appear to be 200 and 500 respectively.

            The value `0` ignores all comments and significantly reduces to time
            required when scanning a subreddit.
=========== =====


extractor.reddit.morecomments
-----------------------------
=========== =====
Type        ``bool``
Default     ``false``
Description Retrieve additional comments by resolving the ``more`` comment
            stubs in the base comment tree.

            This requires 1 additional API call for every 100 extra comments.
=========== =====


extractor.reddit.date-min
-------------------------
=========== =====
Type        ``integer`` (UTC timestamp)
Default     ``0``
Description Ignore all submissions posted before this timestamp.
=========== =====


extractor.reddit.date-max
-------------------------
=========== =====
Type        ``integer`` (UTC timestamp)
Default     ``253402210800`` (timestamp of ``datetime.max``)
Description Ignore all submissions posted after this timestamp.
=========== =====


extractor.reddit.recursion
--------------------------
=========== =====
Type        ``integer``
Default     ``0``
Description Reddit extractors can recursively visit other submissions
            linked to in the initial set of submissions.
            This value sets the maximum recursion depth.

            Special values:

            * ``0``: Recursion is disabled
            * ``-1``: Infinite recursion (don't do this)
=========== =====


extractor.reddit.refresh-token
------------------------------
=========== =====
Type        ``string``
Default     ``null``
Description The ``refresh_token`` value you get from linking your Reddit account
            to ``gallery-dl``.

            Using the ``refresh_token`` allows you to access private or otherwise
            not publicly available subreddits, given that your account is
            authorized to do so,
            but requests to the reddit API are going to be rate limited
            at 600 requests every 10 minutes/600 seconds.
=========== =====


.. |.netrc| replace:: ``.netrc``
.. |tempfile.gettempdir()| replace:: ``tempfile.gettempdir()``
.. |requests.get()| replace:: ``requests.get()``
.. |mature_content| replace:: ``mature_content``
.. |webbrowser.open()| replace:: ``webbrowser.open()``

.. _.netrc:            https://stackoverflow.com/tags/.netrc/info
.. _tempfile.gettempdir(): https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir
.. _requests.get():    https://docs.python-requests.org/en/latest/user/advanced/#timeouts
.. _format string:     https://docs.python.org/3/library/string.html#formatstrings
.. _format strings:    https://docs.python.org/3/library/string.html#formatstrings
.. _mature_content:    https://www.deviantart.com/developers/http/v1/20160316/object/deviation
.. _webbrowser.open(): https://docs.python.org/3/library/webbrowser.html
.. _Authentication:    https://github.com/mikf/gallery-dl#5authentication
