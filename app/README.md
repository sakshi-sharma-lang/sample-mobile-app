# APK Drop Folder

Place the APK under test here.

Default path expected by local runs and GitHub Actions:

```text
app/app-under-test.apk
```

You can override it with:

```bash
APP_PATH=/absolute/path/to/app.apk
```

The APK itself is ignored by Git because release artifacts are normally large, environment-specific, and should be stored in an artifact repository, GitHub release, S3/GCS bucket, or uploaded into the workflow as a CI artifact.
