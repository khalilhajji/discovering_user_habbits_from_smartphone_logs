in the original dataset we noticed a lot of noise and replication coming from the notification feature.
the original data is in /speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/

In this folder we face this problem by taking the original dataset and filtering the notifications without changing or modifying the structure
of the data.

The filtering will be done based on the following criterion:
	- some notifications will be simply blacklisted because they correspond to some internal sony apps and thus not relevant for us
	- the notifications with a low priority will be removed because they are not seen by the user
	- some redundant notifications will be collapsed into one. redundant notifications means the successive records that have the same notifications 
	that is just repeated
	
in the event feature, the event duplicated_notification will be added to signal that a record has been generated due to a duplicate notification
	
	
The blacklisted notifications are:

simply_blocked_apps = {
        "com.google.android.googlequicksearchbox": 1,
        "ginlemon.flowerfree": 1,
        "com.gau.go.launcherex": 1,
        "com.buzzpia.aqua.launcher.buzzhome": 1,
        "com.sony.voyagent.mixs.launcher2": 1,
        "com.sony.voyagent.mixs.hello01": 1,
        "com.sony.voyagent.mixs.icongetter": 1,
        "com.sony.voyagent.mixs.mixswidget": 1,
        "com.sony.voyagent.mixs.packager": 1,
        "com.sony.voyagent.mixs.rawdatalogger": 1,
        "com.sonymobile.genericuploader": 1,
        #"com.sony.activityengine.app.fusedvehicledetectorapp": 1,
        }
