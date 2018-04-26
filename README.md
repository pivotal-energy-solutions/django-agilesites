# Django Agile Sites (django_agilesites)

This provides django the ability of dynamic switching of the settings.SIDE_ID.  This allows
you to then alter the template paths based on the SITE_ID by referencing settings.SITE_FOLDERS.

The way this works is first by dynamically setting (thread-safe) the settings.SITE_ID based on
the request.get_host() (which is based in part on request.META['HTTP_HOST']).  Once the SITE_ID
is established, then it uses that to dynamically look up any template path folder structure you 
define.


## Example / Setup

Lets assume we want to have all traffic going to //beta.foo.com to use our new templates tree
called 'beta' for a new template `app_detail.html`.  This app will allows you to place the
following templates folder structure in your app to achieve this:

    app/
        templates/
            app/
                app_detail.html
                app_list.html
            beta/
                app_detail.html


We need to reference the two sites in question - so in the sites app assume the following.
    SITE_ID: 1  domain: foo.com
    SITE_ID: 2  domain: beta.foo.com

Now to enable this to work you need to do the following:

1.  Add the `django_agilesites` to the settings.INSTALLED_APPS
2.  Add the `django_agilesites.loaders.AgileSiteAppDirectoriesFinder`
to the settings.TEMPLATE_LOADERS.  I put it _first_.
3.  Add the `django_agilesites.middleware.AgileSitesMiddleware'` to the
settings.MIDDLEWARE_CLASSES
4.  Add the following settings to reference the folder beta.


    SITE_FOLDERS = {
        2: 'beta',
    }


That's it.

Now when you go to //beta.foo.com/app/detail you will use the template in the beta tree and when
you go to the list view on beta it will refer to the parent app_list.html.


## Notes:


1.  You do NOT need to reference the SITE_ID 1 as there isn't a path change for that.
2.  You don't have to put every url.  We also support the notion of aliases through the use of
settings.SITE_ALIASES dictionary.  This will force //beta.bar.com to also use the beta templates.


    SITE_ALIASES = {
        'beta.bar.com': 2,
    }

## Versions
-  1.0.x Django 1.8
-  1.1.x Django 1.9 < 2

### Build Process:
1.  Update the `__version_info__` inside of the application. Commit and push.
2.  Tag the release with the version. `git tag <version> -m "Release"; git push --tags`
3.  Build the release `rm -rf dist build *egg-info; python setup.py sdist bdist_wheel`
4.  Upload the data `twine upload dist/*`

Have fun!
