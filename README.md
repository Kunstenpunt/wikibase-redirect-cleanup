# Wikibase Redirect Cleanup

Extremely simple GUI tool that uses WikibaseIntegrator to fix (double) redirects in a wikibase instance.

This tool will not remove the actual redirects themselves (as this information might still be valuable for external references to ids), but it will change all statements in the wikibase instance to directly point to the target value of the redirect. This is what **"Fix statement redirects"** does.

It also has the option to focus on redirects pointing to redirects. It will eventually (multiple runs might be needed) make sure that all these redirects point to the final id in the chain.

`A -> B, B -> C, C -> D` then becomes `A -> D, B -> D, C -> D`

This is what **"Resolve double redirects"** does.

To use, do the following:
- launch the tool
- make sure your wikibase instance settings are entered correctly using the corresponding "Wikibase Instance Config" button (these settings are saved in a `json.config` file next to the executable and will be loaded on subsequent launches)
- add your username and the botpassword
  - username = user that owns the bot (e.g. `WALL-E`)
  - botpassword = BOTNAME@BOTPASSWORD (e.g. `REDIRECTFIXER@123456789`)
- "Fix statement redirects" and "Resolve double redirects" will start a run of that specific cleanup task. Note that you might need to run each multiple times to get all modifications done.

 
Make sure to create a **bot/botpassword with the correct permissions** (basic rights, high-volume (bot) access, editing existing pages). The user itself should also have the **bot** role.
