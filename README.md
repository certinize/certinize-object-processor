# certinize-ecert-processor

## Setup

1. Create a copy of `.env.example` and rename the copy to `.env`.

## ImageKit.io Setup

1. Register at [https://imagekit.io/registration/](https://imagekit.io/registration/)
2. Once registerd, go to your dashboard's [developer options](https://imagekit.io/dashboard/developer/api-keys) where you will find your **Public Key**, **Private Key**, and **URL-endpoint**.
3. Add your keys and URL endpoint as environment variables in your machine or copy and paste them in your `.env` file:

    ```sh
    IMAGEKIT_ENDPOINT_URL=Your ImageKit URL endpoint
    IMAGEKIT_PUBLIC_KEY=Your ImageKit public key
    IMAGEKIT_PRIVATE_KEY=Your ImageKit private key
    ```

## Google Drive API Setup

1. Create a Google Cloud Project. Follow the instructions here: [https://developers.google.com/workspace/guides/create-project](https://developers.google.com/workspace/guides/create-project)
2. Create a Google Service Account for the project you just created. Follow the instructions here: [https://support.google.com/a/answer/7378726?hl=en](https://support.google.com/a/answer/7378726?hl=en)
3. Create a Service Account Key here: [https://console.cloud.google.com/apis/credentials/serviceaccountkey](https://console.cloud.google.com/apis/credentials/serviceaccountkey).
    1. If the page prompts you to select a project, choose the project you just created.
    2. If you see a table that lists the service accounts for the project you selected, click the email of one of the listed service accounts. It should show the details of the service account.
    3. Find and click the *Keys* tab, then find and click the *Add Key* button.
    4. Select *Create new key*.
    5. Select *JSON* as the key type.
    6. Click *Create* and you should see a JSON file being downloaded from your browser.
    7. Once the download completes, open the JSON file. Copy and paste the values to their corresponding environment variables in your machine or `.env` file.

        ```sh
        GDRIVE_SVCS_ACC_PROJECT_ID=""
        GDRIVE_SVCS_ACC_PRIVATE_KEY_ID=""
        GDRIVE_SVCS_ACC_PRIVATE_KEY=""
        GDRIVE_SVCS_ACC_CLIENT_EMAIL=""
        GDRIVE_SVCS_ACC_CLIENT_ID=""
        GDRIVE_SVCS_ACC_AUTH_URI=""
        GDRIVE_SVCS_ACC_TOKEN_URI=""
        GDRIVE_SVCS_ACC_AUTH_PROVIDER_X509_CERT_URL=""
        GDRIVE_SVCS_ACC_CLIENT_X509_CERT_URL=""
        ```
