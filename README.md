My Content Feed
=============

A simple Google AppEngine site to track when the content you are interested in is available online.

All you need to do is supply the index sites to check and the tv show names you are interested in following. A customized RSS feed will be generated for you and automatically updated as soon as new content is found that matches the shows you are interested.


## Installation

1. Download and install the [App Engine SDK for Python][appengine]
2. `git clone git://github.com/cbarbara/MyContentFeed.git`
3. Add your application id to `app.yaml`
4. Open the SDK, choose `File > Add Existing Application...` and select the `MyContentFeed` folder inside the cloned repository
5. Update the settings in `settings.py`
6. Visit http://your-custom-app-id.appspot.com/admin to complete the installation

[appengine]: http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Python

## Development and Testing

To run the unit tests, you will first need to edit the two variables in the file tests/testDownloadZip.py. You will need nose[pythonnose] installed, then run: 

    python2.7 tests/runner.py

[pythonnose]: https://github.com/nose-devs/nose

## Acknowledgements

* slugify by [twillio stashboard](https://github.com/twillio/stashboard)
* bootstrap by [twitter](https://github.com/twitter/bootstrap)
* [feedparser 5.1.2](https://code.google.com/p/feedparser/)
* [nose](https://github.com/nose-devs/nose)
