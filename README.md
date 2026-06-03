# Wikibase Redirect Cleanup

Extremely simple GUI tool that uses WikibaseIntegrator to fix (double) redirects in a wikibase instance.

To use, do the following:
- launch the tool
- make sure your wikibase instance settings are entered correctly using the corresponding "Wikibase Instance Config" button (these settings are saved in a `json.config` file next to the executable and will be loaded on subsequent launches)
- add your username and the botpassword
  - username = user that owns the bot (e.g. `WALL-E`)
  - botpassword = BOTNAME@BOTPASSWORD (e.g. `REDIRECTFIXER@123456789`)
- "Fix statement redirects" will query all redirects, and change them directly to their redirected value.
- "Resolve double redirects" will specifically only focus on redirects *to redirects*, and make sure to point directly to the target. This is a subset of all redirects. It can be necessary to run this multiple times in order to also resolve longer redirect chains. This is useful as a separate function because wikibase actually handles single redirects well, but struggles with longer redirect chains. It is faster to remove only the double redirects than removing *all* redirects, what the previous button attempts to do.
 
Make sure to create a **bot/botpassword with the correct permissions** (basic rights, high-volume (bot) access, editing existing pages). The user itself should also have the **bot** role.
