---
source: https://developers.mekari.com/docs/kb
title: Home - Mekari Developers Documentation
---

# Mekari Developers Documentation

Explore our guides and examples to integrate Mekari products.

### Getting Started

Build integration between your internal application with robust Mekari APIs with few simple steps.

[Create Your First Application](/docs/kb/managing-applications/create-application)

### Deep Dive into HMAC

HMAC is [simple key-based authentication method](https://en.wikipedia.org/wiki/HMAC) allowing for faster integration with your business.

[Learn More](/docs/kb/hmac-authentication)

### Browse the APIs

Jump immediately to the APIs and see what kind the integration you want to achieve.

[Postman Collections](/docs/kb/product-api)

---



---
source: https://developers.mekari.com/docs/kb/managing-applications
title: Managing Applications - Mekari Developers Documentation
---

# Managing Applications

---

## Table of contents

* [Create Application](/docs/kb/managing-applications/create-application)

---



---
source: https://developers.mekari.com/docs/kb/managing-applications/create-application
title: Create Application - Mekari Developers Documentation
---

# Create Your First Application

## Request Access

Before continue on this guide, you need to make sure that your account has been authorized to Mekari Developer. To check it you can login login then if your dashboard show an empty page, this means you account has not been authorized. Please contact your specialist or support if you want to access to Mekari Developer.

### For Talenta Company

To start the integration, please contact our team, by providing your email, company\_name & company\_id to talenta-integration[at]mekari.com. The email must be registered and can access the company\_name or company\_id on <https://hr.talenta.co/>

Next, we will notice if your email has been successfully registered to [Mekari Developer](https://developers.mekari.com/) and once registered, you can generate HMAC and connect to Talenta API by following the instruction below.

## Create Application

On Mekari Developer dashboard, you will see “Create Application” button on the top near header. Click the button and you will be redirected to a page where you can create an application.

On the page, you will see 3 fields:

* Application Name* Company* Authorized Scopes

**Application Name** is a field where you need to enter the name of your application. You can set the name into anything you want, but make sure that it reflect your application. Most of the time, people fill it with the name of their internal company application.

**Company** is a field where you need to select the company you want to develop integration into. You are only allowed to select one company on this field. If you happen to have more than one company and you want to setup integration to all of it, you need to create application for each company and get separated client credentials.

**Authorized Scopes** is a field where you need to tick the scopes you need for the integration. Each scope represent specific API endpoint. Please only choose only scope that you need for your company internal application. To learn more about application scopes, please visit [this page](#).

Once you fill all the fields, click submit to create client credentials for your application.

## Client Credentials

After you create the application, Client ID and Client Secret your application will appear on the page. Make sure you copy the credentials especially Client Secret, because you only able to see the value of client secret on this page.

From here you can use the credentials to integrate your application with Mekari API. You can see examples on how to setup HMAC authentication on [this section](/docs/kb/hmac-authentication).

---



---
source: https://developers.mekari.com/docs/kb/hmac-authentication
title: HMAC Authentication - Mekari Developers Documentation
---

# HMAC Authentication

## Overview

HMAC (Hash-based Message Authentication Code) is an authentication protocol that allows you to integrate the Mekari API faster than OAuth2. However, an HMAC credential (consisting of `CLIENT ID` and `CLIENT SECRET`) is tied to one specific company, which means you can only perform API requests that are limited to your company data in Mekari Product.

For example, if your company is already a Talenta subscriber and you want to get a list of your employees who have registered on Talenta, you’ll need new HMAC client credentials with the appropriate scopes. Using these credentials, you can generate an HMAC signature and attach it to your request header when making an API call to one of our API endpoints.

If you have multiple Mekari product subscriptions, you must have HMAC client credentials for each company in order to successfully perform API calls to our API endpoints.

Currently, one HMAC credential is also limited to each Mekari product, which means that if your company subscribes to multiple Mekari products (for example, Talenta and [Klikpajak](https://klikpajak.id)), you must create one HMAC credential for each product API you wish to access.

## HMAC Credentials

We are currently developing a platform that will allow you to create your own HMAC credentials. For the time being, if you require HMAC credentials, please contact our customer support or a product specialist. From there, we will assist you in creating new HMAC credentials for your company as well as selecting the appropriate application scopes for the credentials.

## API Availability

Not all Mekari product API endpoints can be accessed via HMAC authentication. Please visit our Product API section to learn more about the APIs available for HMAC authentication.

## Authorization Header

When using HMAC authentication to call Mekari API endpoints, the `Authorization` header is required. We expect your application to send the `Authorization` header with the following parameterization.

```
credentials := "hmac" params
params := keyId "," algorithm ", " headers ", " signature
keyId := "username" "=" plain-string
algorithm := "algorithm" "=" "hmac-sha256"
headers := "headers" "=" "date request-line"
signature := "signature" "=" plain-string
plain-string   = DQUOTE *( %x20-21 / %x23-5B / %x5D-7E ) DQUOTE
```

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| parameter description|  |  |  |  |  |  |  |  | | --- | --- | --- | --- | --- | --- | --- | --- | | username The `CLIENT_ID` of the HMAC credential| algorithm Digital signature algorithm used to create the signature, in this case `hmac-sha256`.| headers List of HTTP header names, separated by a single space character, used to sign the request. In this case `date` and `request-line`| signature Base64 encoded digital signature generated by your application. | | | | | | | | | |

An example of an authorization header on your application request is as follows:

```
Authorization: hmac username="YOUR_CLIENT_ID", algorithm="hmac-sha256", headers="date request-line", signature="xxxx"
```

## Generating Signature

You must have a signature on your API request, as you can see from the parameter and the example above. The following code (pseudocode) was used to generate this signature:

```
function generate_hmac_auth_token:
    input:
        client_id: string
        client_secret: string
        base_url: string 
        pathWithQueryParam: string
        http_method: string 

    date_rfc_1123 = now().format(RFC7231)
    signing_string = "date: \n  HTTP/1.1"
    digest = HMAC-SHA256(signing_string, client_secret)
    base64_digest = base64(digest)
    hmac_auth_token = `hmac username="", algorithm="hmac-sha256", headers="date request-line", signature=""`

    return hmac_auth_token
```

Please see our code examples section for a specific implementation in your preferred programming language.

## Date Header

Along with the Authorization header, you must also include the Date header in your API request. It must have the current datetime in UTC timezone, as specified in [RFC7231](https://datatracker.ietf.org/doc/html/rfc7231#section-7.1.1.1). If you look at the above signature generation, you will notice that it also uses a datetime string, and the value between that and the Date header must be the same.

An example of a Date header:

```
Date: Sun, 06 Nov 1994 08:49:37 GMT
```

The `Date` header is also used to prevent replay attacks and has a clock skew of 300 seconds. It means that the time difference between the time you send the API call and the datetime you specify in the `Date` header and the signature must be less than 300 seconds. Otherwise, the request will be rejected.

## Body Validation

You need to provide Body Validation on your API request. This is because we need protect the API call from Man-in-the-Middle attacks (MITM). To do this, you need add a new header to your request called `Digest`, which contains the SHA-256 hash of your request body, which is required when performing a `POST`, `PUT`, `PATCH`, or `DELETE` request.

The `Digest` header should be formatted as follows:

```
digest=SHA-256(body)
base64_digest=base64(digest)
Digest: SHA-256=<base64_digest>
```

In [cURL](https://curl.se/), this is an example of the `Digest` header:

```
curl --request POST 'https://examples.com/foo/bar' \
--header 'Digest: X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=' \
--data-raw '{"hello": "world"}'
```

Please keep in mind that the content of the `Digest` header is determined by the body of your request. This means you probably don’t want to use the `Digest` header on API calls that require a large request body, such as APIs that require an upload file, because it will generate a larger Digest value.

Please see our code examples section for a specific implementation in your preferred programming language.

## Final Result

After you’ve met all of the prerequisites listed above, your API request should look like this in cURL format:

```
curl --request POST 'https://examples.com/foo/bar?hello=world' \
--header 'Authorization: hmac username="CLIENT_ID", algorithm="hmac-sha256", headers="date request-line", signature="r70pUQMDXWaFUEWPybBbn9d+ae2naufbIckiT6wcAio="' \
--header 'Date: Tue, 24 Aug 2021 02:18:19 GMT' \
--header 'Content-Type: application/json' \
--header 'Digest: SHA-256=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE=' \
--data-raw '{"hello": "world"}'
```

The actual implementation may differ depending on the programming language used. Please consider looking at to see the examples of the code below.

---

## Table of contents

* [PHP](/docs/kb/hmac-authentication/php)* [Node.js](/docs/kb/hmac-authentication/node)* [Ruby](/docs/kb/hmac-authentication/ruby)* [Java 8](/docs/kb/hmac-authentication/java)

---



---
source: https://developers.mekari.com/docs/kb/hmac-authentication/php
title: PHP - Mekari Developers Documentation
---

# Setup HMAC Authentication in PHP

We will be using [PHP](https://www.php.net/manual/en/install.php) version 8 (v8.0.12) and [Composer](https://getcomposer.org/) version 2 (v2.1.11). We assume you are already familiar with PHP and have Composer installed on your system. Let’s get started.

## Install Dependencies

Because we’ll be using Composer, make sure you have the `composer.json` file in your working directory. If you don’t have the file, make one with the following content:

```
{
    "require": {}
}
```

There will be three dependency: [GuzzleHTTP](https://docs.guzzlephp.org/en/stable/index.html) to make HTTP requests to the Mekari API, [Carbon](https://carbon.nesbot.com/) to handle datetime formatting for generating HMAC signatures, and [phpdotenv](https://github.com/vlucas/phpdotenv) for environment variable loader, because we don’t want to put the Mekari API client ID and client secret directly on the code.

```
$ php composer.phar require guzzlehttp/guzzle:^7.0 nesbot/carbon vlucas/phpdotenv
```

Once installed, your `require` attribute on the `composer.json` will look something like this.

```
{
    "require": {
        "guzzlehttp/guzzle": "^7.0",
        "nesbot/carbon": "^2.54",
        "vlucas/phpdotenv": "^5.3"
    }
}
```

## Making API Request

Using GuzzleHTTP that we have installed earlier, we are going to setup PHP script that will perform API request to one of [Klikpajak](https://klikpajak.id) API endpoint which is [create sales invoice](https://documenter.getpostman.com/view/17365057/U16hrR5d#63ba32aa-0f91-44a5-ab40-a0da6a8bf608) (`https://api.mekari.com/v2/klikpajak/v1/efaktur/out`).

We create the script called `main.php` then use GuzzleHTTP to perform the HTTP POST request. Since we are using Composer, we need to make sure we put the autoload file on the top of the script. This is how the script will looks like:

```
<?php // main.php

require 'vendor/autoload.php';

$client = new GuzzleHttp\Client([
    'base_uri' => 'https://api.mekari.com/v2/klikpajak/v1'
]);

$response = $client->request('POST', 'efaktur/out?auto_approval=false');
```

We can run the script on the console by typing `php main.php`. Because we just created a plain HTTP POST request, it will throw an error similar to this:

```
$ php main.php
PHP Fatal error:  Uncaught GuzzleHttp\Exception\ClientException: Client error: `POST https://api.mekari.com/v2/klikpajak/efaktur/out?auto_approval=false` resulted in a `401 Unauthorized` response:
{"message":"Unauthorized"}
 in /working/directory/vendor/guzzlehttp/guzzle/src/Exception/RequestException.php:113
Stack trace: ...
```

Before we add authentication to the request, let’s catch the error and display it nicely on the console.

```
<?php // main.php

require 'vendor/autoload.php';

use GuzzleHttp\Psr7;
use GuzzleHttp\Exception\ClientException;

$client = new GuzzleHttp\Client([
    'base_uri' => 'https://api.mekari.com/v2/klikpajak/v1'
]);

try {
    $response = $client->request('POST', 'efaktur/out?auto_approval=false');
} catch (ClientException $e) {
    echo Psr7\Message::toString($e->getRequest());
    echo Psr7\Message::toString($e->getResponse());
    echo PHP_EOL;
}
```

When we run the script again, the error message will be as follows:

```
$ php main.php
POST /v2/klikpajak/efaktur/out?auto_approval=false HTTP/1.1
User-Agent: GuzzleHttp/7
Host: api.mekari.com

HTTP/1.1 401 Unauthorized
date: Tue, 09 Nov 2021 02:37:41 GMT
content-type: application/json; charset=utf-8
content-length: 26
x-envoy-upstream-service-time: 0
server: Mekari

{"message":"Unauthorized"}
```

## Creating HMAC Signature

[The signature](/docs/kb/authentication/hmac#generating-signature) is one of the requirements for forming an API request with HMAC Authentication. The signature is an HMAC256 representation of the request line (a combination of the request method, the request path, the query param, and `HTTP/1.1`) and the `Date` header in [RFC 7231](https://www.ietf.org/rfc/rfc7231.txt) format. Carbon will be used to generate the date string for us. The signature must then be converted into a Base64 string so that it can be attached to the `Authorization` header.

The code will look like this:

```
<?php // main.php

use Carbon\Carbon;

// ... the rest of the code

$datetime       = Carbon::now()->toRfc7231String();
$request_line   = "POST /v2/klikpajak/v1/efaktur/out?auto_approval=false HTTP/1.1";
$payload        = implode("\n", ["date: {$datetime}", $request_line]);
$digest         = hash_hmac('sha256', $payload, 'YOUR_MEKARI_CLIENT_SECRET', true);
$signature      = base64_encode($digest);

echo "hmac username=\"YOUR_MEKARI_API_CLIENT_ID\", algorithm=\"hmac-sha256\", headers=\"date request-line\", signature=\"{$signature}\"";
```

If you replace `$datetime` with `Wed, 10 Nov 2021 07:24:29 GMT` and run the code, you will get the following result.

```
$ php main.php
hmac username="YOUR_MEKARI_API_CLIENT_ID", algorithm="hmac-sha256", headers="date request-line", signature="6+Ah/UTmbqd+DDqlh6zYZ0HuCwVhtElYDOoucRPCaFg="
```

It is important to note that we should not include any credentials in our codebase. This means that we must save the Mekari API client id and client secret that you obtained from the Mekari Developer dashboard to an environment variable. Modern full-stack frameworks, such as Laravel, usually include an `.env` file to make managing environment variables easier. This is also why phpdotenv was installed. We can use this library to move the client id and client secret to the `.env` file.

```
# .env file
MEKARI_API_CLIENT_ID=YOUR_MEKARI_API_CLIENT_ID
MEKARI_API_CLIENT_SECRET=YOUR_MEKARI_CLIENT_SECRET
MEKARI_API_BASE_URL=https://api.mekari.com
```

Then we use `$_ENV[]` to replace the credentials in the code.

```
<?php // main.php

use Carbon\Carbon;
use Dotenv\Dotenv;

$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

// ... the rest of the code

$datetime       = Carbon::now()->toRfc7231String();
$request_line   = "POST /v2/klikpajak/v1/efaktur/out?auto_approval=false  HTTP/1.1";
$payload        = implode("\n", ["date: {$datetime}", $request_line]);
$digest         = hash_hmac('sha256', $payload, $_ENV['MEKARI_API_CLIENT_SECRET'], true);
$signature      = base64_encode($digest);

echo "hmac username=\"{$_ENV['MEKARI_API_CLIENT_ID']}\", algorithm=\"hmac-sha256\", headers=\"date request-line\", signature=\"{$signature}\"";
```

## Wrap It Out

It’s now time to combine everything we’ve learned into a single PHP script.

```
<?php

require 'vendor/autoload.php';

use Carbon\Carbon;
use Dotenv\Dotenv;
use GuzzleHttp\Psr7\Request;
use GuzzleHttp\Psr7;
use GuzzleHttp\Exception\ClientException;

// Load .env file
$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

/**
 * Generate authentication headers based on method and path
 */
function generate_headers($method, $pathWithQueryParam) {
    $datetime       = Carbon::now()->toRfc7231String();
    $request_line   = "{$method} {$pathWithQueryParam} HTTP/1.1";
    $payload        = implode("\n", ["date: {$datetime}", $request_line]);
    $digest         = hash_hmac('sha256', $payload, $_ENV['MEKARI_API_CLIENT_SECRET'], true);
    $signature      = base64_encode($digest);
    
    return [
        'Accept'        => 'application/json',
        'Content-Type'  => 'application/json',
        'Date'          => $datetime,
        'Authorization' => "hmac username=\"{$_ENV['MEKARI_API_CLIENT_ID']}\", algorithm=\"hmac-sha256\", headers=\"date request-line\", signature=\"{$signature}\""
    ];
}

// Set http client
$client = new GuzzleHttp\Client([
    'base_uri' => $_ENV['MEKARI_API_BASE_URL']
]);

$method     = 'POST';
$path       = '/v2/klikpajak/v1/efaktur/out';
$queryParam = '?auto_approval=false';
$headers    = [
    'X-Idempotency-Key' => '1234'
];
$body       = [/* request body */];

// Initiate request
try {
    $response = $client->request($method, $path . $queryParam, [
        'headers'   => array_merge(generate_headers($method, $path . $queryParam), $headers),
        'body'      => json_encode($body)
    ]);

    echo $response->getBody();
} catch (ClientException $e) {
    echo Psr7\Message::toString($e->getRequest());
    echo Psr7\Message::toString($e->getResponse());
    echo PHP_EOL;
}
```

If you want to integrate this script with your existing code, you may need to modify it. Additionally, each Mekari API has its own requirements regarding request headers, query, or body, and you may need to change the script based on your needs. We hope that this guide makes integrating Mekari API into your code easier for you.

You can also look at the final code on [this repository](https://github.com/mekari-engineering/mekari-api-hmac-example-php).

---



---
source: https://developers.mekari.com/docs/kb/hmac-authentication/node
title: Node.js - Mekari Developers Documentation
---

# Setup HMAC Authentication in Node.js

We will be using [Node.js](https://nodejs.org/en/download/) version 16 (v16.13.0) and [npm](https://getcomposer.org/) version 8 (v8.1.0). We assume you are already familiar with Node.js and have npm installed on your system. Let’s get started.

## Install Dependencies

Because we’ll be using npm, make sure you have the `package.json` file in your working directory. If you don’t have the file, make one by running this command `npm init`. Then you will be asked couple question regarding your npm project and once it done the content of the file will look like this:

```
{
  "name": "your-node-project",
  "version": "0.1.0",
  "description": "Your project description",
  "main": "main.js",
  "author": "Your Name <your-email@example.com>",
  "dependencies": {}
}
```

There will be two dependency: [Axios](https://axios-http.com/) to make HTTP requests to the Mekari API and [dotenv](https://github.com/motdotla/dotenv) for environment variable loader, because we don’t want to put the Mekari API client ID and client secret directly on the code.

```
$ npm add axios dotenv --save
```

Once installed, your `dependencies` attribute on the `package.json` will look something like this.

```
{
  "dependencies": {
    "axios": "^0.24.0",
    "dotenv": "^10.0.0"
  }
}
```

## Making API Request

Using Axios that we have installed earlier, we are going to setup a script that will perform API request to one of [Klikpajak](https://klikpajak.id) API endpoint which is [create sales invoice](https://documenter.getpostman.com/view/17365057/U16hrR5d#63ba32aa-0f91-44a5-ab40-a0da6a8bf608) (`https://api.mekari.com/v2/klikpajak/v1/efaktur/out`) with query param `?auto_approval=false`.

We create the script called `main.js` then use Axios to perform the HTTP POST request. This is how the script will looks like:

```
const axios = require('axios');

axios({
  method: 'POST',
  url: 'https://api.mekari.com/v2/klikpajak/v1/efaktur/out?auto_approval=false'
}).then(function (response) {
    console.log(response.data);
  })
  .catch(function (error) {
    console.log(error);
  });
```

We can run the script on the console by typing `node main.js`. Because we just created a plain HTTP POST request, it will throw an error similar to this:

```
$ node main.js
{
  {
    // ...a lot of data
    data: { message: 'Unauthorized' }
  },
  isAxiosError: true,
  toJSON: [Function: toJSON]
}
```

Before we add authentication to the request, let’s catch the error and display it nicely on the console.

```
const axios = require('axios');

axios({
  method: 'POST',
  url: 'https://api.mekari.com/v2/klikpajak/v1/efaktur/out?auto_approval=false'
}).then(function (response) {
    console.log(response.data);
  })
  .catch(function (error) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.log(error.response.data);
      console.log(error.response.status);
      console.log(error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.log(error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.log('Error', error.message);
    }
  });
```

When we run the script again, the error message will be as follows:

```
$ node main.js
{ message: 'Unauthorized' }
401
{
  date: 'Thu, 25 Nov 2021 02:21:08 GMT',
  'content-type': 'application/json; charset=utf-8',
  'content-length': '26',
  'x-envoy-upstream-service-time': '2',
  server: 'Mekari',
  connection: 'close'
}
```

## Creating HMAC Signature

[The signature](/docs/kb/authentication/hmac#generating-signature) is one of the requirements for forming an API request with HMAC Authentication. The signature is an HMAC256 representation of the request line (a combination of the request method, the request path, the query param and `HTTP/1`.1) and the `Date` header in [RFC 7231](https://www.ietf.org/rfc/rfc7231.txt) format. The signature must then be converted into a Base64 string so that it can be attached to the `Authorization` header.

The code will look like this:

```
// ... the rest of the code

const datetime = new Date().toUTCString();
const requestLine = "POST /v2/klikpajak/v1/efaktur/out?auto_approval=false  HTTP/1.1";
const payload = [`date: ${datetime}`, requestLine].join('\n');
const signature = crypto.createHmac('SHA256', 'YOUR_MEKARI_CLIENT_SECRET').update(payload).digest('base64');

console.log(`hmac username="YOUR_MEKARI_CLIENT_ID", algorithm="hmac-sha256", headers="date request-line", signature="${signature}"`)
```

If you replace `datetime` with `Wed, 10 Nov 2021 07:24:29 GMT` and run the code, you will get the following result.

```
$ node main.js
hmac username="YOUR_MEKARI_CLIENT_SECRET", algorithm="hmac-sha256", headers="date request-line", signature="6+Ah/UTmbqd+DDqlh6zYZ0HuCwVhtElYDOoucRPCaFg="
```

It is important to note that we should not include any credentials in our codebase. This means that we must save the Mekari API client id and client secret that you obtained from the Mekari Developer dashboard to an environment variable. Modern full-stack frameworks, such as Laravel, usually include an `.env` file to make managing environment variables easier. This is also why phpdotenv was installed. We can use this library to move the client id and client secret to the `.env` file.

```
# .env file
MEKARI_API_BASE_URL=https://api.mekari.com
MEKARI_API_CLIENT_ID=YOUR_MEKARI_API_CLIENT_ID
MEKARI_API_CLIENT_SECRET=YOUR_MEKARI_CLIENT_SECRET
```

Then we use `process.env.*` to replace the credentials in the code.

```
const axios = require('axios');
const crypto = require('crypto');

require('dotenv').config();

// ... the rest of the code

const datetime = new Date().toUTCString();
const requestLine = "POST /v2/klikpajak/v1/efaktur/out?auto_approval=false  HTTP/1.1";
const payload = [`date: ${datetime}`, requestLine].join('\n');
const signature = crypto.createHmac('SHA256', process.env.MEKARI_API_CLIENT_SECRET).update(payload).digest('base64');

console.log(`hmac username="${process.env.MEKARI_API_CLIENT_ID}", algorithm="hmac-sha256", headers="date request-line", signature="${signature}"`)
```

## Wrap It Out

It’s now time to combine everything we’ve learned into a single Node.js script.

```
const axios = require('axios');
const crypto = require('crypto');

require('dotenv').config();

/**
 * Generate authentication headers based on method and path
 */
function generate_headers(method, pathWithQueryParam) {
  let datetime = new Date().toUTCString();
  let requestLine = `${method} ${pathWithQueryParam} HTTP/1.1`;
  let payload = [`date: ${datetime}`, requestLine].join("\n");
  let signature = crypto.createHmac('SHA256', process.env.MEKARI_API_CLIENT_SECRET).update(payload).digest('base64');

  return {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Date': datetime,
    'Authorization': `hmac username="${process.env.MEKARI_API_CLIENT_ID}", algorithm="hmac-sha256", headers="date request-line", signature="${signature}"`
  };
}

// Set method and path for the request
let method = 'POST';
let path = '/v2/klikpajak/v1/efaktur/out';
let queryParam = '?auto_approval=false';
let headers = {
  'X-Idempotency-Key': '1234'
};
let body = {/* request body */};

const options = {
  method: method,
  url: `${process.env.MEKARI_API_BASE_URL}${path}${queryParam}`,
  headers: {...generate_headers(method, path + queryParam), ...headers}
}

// Initiate request
axios(options)
  .then(function (response) {
    console.log(response.data);
  })
  .catch(function (error) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.log(error.response.data);
      console.log(error.response.status);
      console.log(error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.log(error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.log('Error', error.message);
    }
  });
```

If you want to integrate this script with your existing code, you may need to modify it. Additionally, each Mekari API has its own requirements regarding request headers, query, or body, and you may need to change the script based on your needs. We hope that this guide makes integrating Mekari API into your code easier for you.

You can also look at the final code on [this repository](https://github.com/mekari-engineering/mekari-api-hmac-example-node).

---



---
source: https://developers.mekari.com/docs/kb/hmac-authentication/ruby
title: Ruby - Mekari Developers Documentation
---

# Setup HMAC Authentication in Ruby

We will be using [Ruby](https://www.ruby-lang.org) version 2.7 (v2.7.4) and [Bundler](https://bundler.io) version 2.1.4. We assume you are already familiar with Ruby and have Bundler installed on your system. Let’s get started.

## Install Dependencies

Because we’ll be using Bundle, make sure you have the `Gemfile` file in your working directory. If you don’t have the file, make one with the following content:

```
source "https://rubygems.org"

git_source(:github) { |repo_name| "https://github.com/#{repo_name}" }
```

We will need to add faraday to Gemfile [Faraday](https://lostisland.github.io/faraday) for HTTP requests to the Mekari API.

```
# Gemfile
gem 'faraday'
```

And we will put all credentials on .env since we don’t want to Mekari API client ID and client secret exposed directly on the code. To load the .env, we will need [Doetenv](https://github.com/bkeepers/dotenv) .

```
# Gemfile
gem 'dotenv'
```

## Making API Request

Using Faraday and Dotenv that we have installed earlier, we are going to setup Ruby script that will perform API request to one of [Klikpajak](https://klikpajak.id) API endpoint which is [create sales invoice](https://documenter.getpostman.com/view/17365057/U16hrR5d#63ba32aa-0f91-44a5-ab40-a0da6a8bf608) (`https://api.mekari.com/v2/klikpajak/v1/efaktur/out`).

We create the script called `main.rb` then use Faraday to perform the HTTP POST request. This is how the script will looks like:

```
path = '/v2/klikpajak/v1/efaktur/out/'
queryParam = '?auto_approval=false'
headers = { 'X-Idempotency-Key' => '1234' }
response = Faraday.post("#{ENV['MEKARI_API_BASE_URL']}/#{path}", nil, headers)

puts "Got response with status: #{response.status}, body: #{response.body}"
```

We can run the script on the console by typing `ruby main.rb`. Because we just created a plain HTTP POST request, it will has an error response similar to this:

```
$ ruby main.rb
Got response with status: 401, body: {"message":"Unauthorized"}
```

## Creating HMAC Signature

[The signature](/docs/kb/authentication/hmac#generating-signature) is one of the requirements for forming an API request with HMAC Authentication. The signature is an HMAC256 representation of the request line (a combination of the request method, the request path, the query params and `HTTP/1.1`) and the `Date` header in [RFC 7231](https://www.ietf.org/rfc/rfc7231.txt) format. Carbon will be used to generate the date string for us. The signature must then be converted into a Base64 string so that it can be attached to the `Authorization` header.

The code will look like this:

```
// ... the rest of the code

datetime = Time.now.httpdate
request_line = "POST /v2/klikpajak/v1/efaktur/out?auto_approval=false HTTP/1.1"
payload = ["date: #{datetime}", request_line].join("\n")
digest = OpenSSL::HMAC.digest(OpenSSL::Digest.new('sha256'), 'YOUR_MEKARI_API_CLIENT_SECRET', payload)
signature = Base64.strict_encode64(digest)

puts "hmac username=\"YOUR_MEKARI_API_CLIENT_ID", algorithm=\"hmac-sha256\", headers=\"date request-line\", signature=\"#{signature}\""
```

If you replace `datetime` with `Wed, 10 Nov 2021 07:24:29 GMT` and run the code, you will get the following result.

```
$ ruby main.rb
hmac username="YOUR_MEKARI_API_CLIENT_ID", algorithm="hmac-sha256", headers="date request-line", signature="6+Ah/UTmbqd+DDqlh6zYZ0HuCwVhtElYDOoucRPCaFg="
```

It is important to note that we should not include any credentials in our codebase. This means that we must save the Mekari API client id and client secret that you obtained from the Mekari Developer dashboard to an environment variable. Modern full-stack frameworks, such as Laravel, usually include an `.env` file to make managing environment variables easier. This is also why Dotenv was installed. We can use this library to move the client id and client secret to the `.env` file.

```
# .env file
MEKARI_API_CLIENT_ID=YOUR_MEKARI_API_CLIENT_ID
MEKARI_API_CLIENT_SECRET=YOUR_MEKARI_CLIENT_SECRET
```

Then we use `ENV` to replace the credentials in the code.

```
// main.rb

require 'time'
require 'base64'
require 'openssl'
require 'faraday'

// ... the rest of the code

datetime = Time.now.httpdate
request_line = "POST /v2/klikpajak/v1/efaktur/out?auto_approval=false HTTP/1.1"
payload = ["date: #{datetime}", request_line].join("\n")
digest = OpenSSL::HMAC.digest(OpenSSL::Digest.new('sha256'), ENV['MEKARI_API_CLIENT_SECRET'], payload)
signature = Base64.strict_encode64(digest)

puts "hmac username=\"#{ENV['MEKARI_API_CLIENT_ID']}", algorithm=\"hmac-sha256\", headers=\"date request-line\", signature=\"#{signature}\""
```

## Wrap It Out

It’s now time to combine everything we’ve learned into a single Ruby script.

```
require 'time'
require 'base64'
require 'openssl'
require 'faraday'
require 'dotenv'

Dotenv.load

# Generate headers to be used on API call.
#
# @return [Hash<String, Object>]
def generate_headers(method, pathWithQueryParam)
  datetime = Time.now.httpdate
  request_line = "#{method} #{pathWithQueryParam} HTTP/1.1"
  payload = ["date: #{datetime}", request_line].join("\n")
  digest = OpenSSL::HMAC.digest(OpenSSL::Digest.new('sha256'), ENV['MEKARI_API_CLIENT_SECRET'], payload)

  signature = Base64.strict_encode64(digest)

  {
    'Content-Type' => 'application/json',
    'Date' => datetime,
    'Authorization' => "hmac username=\"#{ENV['MEKARI_API_CLIENT_ID']}\", algorithm=\"hmac-sha256\", headers=\"date request-line\", signature=\"#{signature}\""
  }
end

# Set method and path for the request
method = 'POST'
path = '/v2/klikpajak/v1/efaktur/out'
queryParam = '?auto_approval=false'
default_headers = { 'X-Idempotency-Key' => '1234' }
request_headers = default_headers.merge(generate_headers(method, path + queryParam))

puts "Start request with url: #{ENV['MEKARI_API_BASE_URL']}#{path}, headers: #{request_headers}"

conn = Faraday.new(url: ENV['MEKARI_API_BASE_URL']) do |faraday|
  faraday.response :logger # log requests and responses to $stdout
end

response = conn.post(path, nil, request_headers)

puts "Got response with status: #{response.status}, body: #{response.body}"
```

If you want to integrate this script with your existing code, you may need to modify it. Additionally, each Mekari API has its own requirements regarding request headers, query, or body, and you may need to change the script based on your needs. We hope that this guide makes integrating Mekari API into your code easier for you.

You can also look at the final code on [this repository](https://github.com/mekari-engineering/mekari-api-hmac-example-ruby).

---



---
source: https://developers.mekari.com/docs/kb/hmac-authentication/java
title: Java 8 - Mekari Developers Documentation
---

# Setup HMAC Authentication in Java 8

We will be using [Java 8](https://www.java.com/en/download/) and use [maven](https://maven.apache.org/download.cgi) to manage dependency. We assume you are already familiar with Java and have it installed on your system. Let’s get started.

## Install Dependencies

Because we’ll be using maven, make sure you have the `pom.xml` file in the root of your working directory. The content of the file should look like this:

```
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.example</groupId>
    <artifactId>HMAC Signature</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
    </properties>

    <dependencies>
        ...
    </dependencies>

</project>
```

There will be only one dependency: [OkHttp](https://square.github.io/okhttp/4.x/okhttp/okhttp3/) to make HTTP requests to the Mekari API. There are many Http Client Library out there and you can also choose any other clients.

To install the dependency simply add it under `dependencies` attribute on the `pom.xml`. The file will look something like this.

```
<dependencies>
    <dependency>
        <groupId>com.squareup.okhttp3</groupId>
        <artifactId>okhttp</artifactId>
        <version>4.9.1</version>
    </dependency>
</dependencies>
```

## Making API Request

Using OkHttp Client that we have installed earlier, we are going to setup a script that will perform API request to one of [Klikpajak](https://klikpajak.id) API endpoint which is [create sales invoice](https://documenter.getpostman.com/view/17365057/U16hrR5d#63ba32aa-0f91-44a5-ab40-a0da6a8bf608) (`https://api.mekari.com/v2/klikpajak/v1/efaktur/out`).

We create the script inside the main function:

```
public static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

public static void main(String[] args) {

    OkHttpClient client = new OkHttpClient();

    //      Request Base URL
    String base = "https://api.mekari.com";

    //      HMAC User client id
    String clientId = System.getenv("MEKARI_API_CLIENT_ID");

    //      HMAC User client secret
    String clientSecret = System.getenv("MEKARI_API_CLIENT_SECRET");

    //      Request method GET/POST/PUT/DELETE
    String method = "POST";

    //      Request endpoint
    String path = "/v2/klikpajak/v1/efaktur/out";

    String queryParam = "?auto_approval=false";

    //      Request Body
    String json = "requestBody";

    RequestBody body = RequestBody.create(json, JSON); 

    Request request = new Request.Builder()
        .url(base + path + queryParam)
        .post(body)
        .build();

    Call call = client.newCall(request);
    try {
        Response response = call.execute();
        System.out.println(response.body().string());
    } catch (IOException e) {
        e.printStackTrace();
    }
}
```

We can try run the script now but will immediately get Unauthorized response due to no authentication attached in the request.

```
{"message":"Unauthorized"}
```

## Creating HMAC Signature

[The signature](/docs/kb/authentication/hmac#generating-signature) is one of the requirements for forming an API request with HMAC Authentication. The signature is an HMAC256 representation of the request line (a combination of the request method, the request path, the query param and `HTTP/1.1`) and the `Date` header in [RFC 7231](https://www.ietf.org/rfc/rfc7231.txt) format. The signature must then be converted into a Base64 string so that it can be attached to the `Authorization` header.

The full request will look like this:

```
// ... the rest of the code

//      Request Date
String dateFormatted = getDateTimeNowUtcString();
        
Request request = new Request.Builder()
    .url(base + path + queryParam)
    .post(body)
    .addHeader("Date", dateFormatted)
    .addHeader("Authorization",
        generateAuthSignature(clientId, clientSecret, method, path + queryParam, dateFormatted)
    )
    .build();

Call call = client.newCall(request);
```

To get Date following RFC 7231 format we use this function

```
private static String getDateTimeNowUtcString() {
    Instant instant = Instant.now();
    return DateTimeFormatter.ofPattern("EEE, dd MMM yyyy HH:mm:ss O")
        .withZone(ZoneOffset.UTC)
        .withLocale(Locale.US)
        .format(instant);
}
```

To generate the Authorization Header we use these functions

```
import java.nio.charset.StandardCharsets;

private static String generateAuthSignature(
    String clientId, String clientSecret, String method,
    String pathWithQueryParam, String dateString
) {
    String payload = generatePayload(pathWithQueryParam, method, dateString);
    String signature = hmacSha256(clientSecret, payload);

    return "hmac username=\"" + clientId
        + "\", algorithm=\"hmac-sha256\", headers=\"date request-line\", signature=\""
        + signature + "\"";
}

private static String generatePayload(String pathWithQueryParam, String method, String dateString) {
    String requestLine = method + ' ' + pathWithQueryParam + " HTTP/1.1";
    return String.join("\n", Arrays.asList("date: " + dateString, requestLine));
}

private static String hmacSha256(String clientSecret, String payload) {
    try {
        SecretKeySpec signingKey = new SecretKeySpec(clientSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(signingKey);

        return Base64.getEncoder().encodeToString(mac.doFinal(payload.getBytes(StandardCharsets.UTF_8)));
    } catch (NoSuchAlgorithmException | UnsupportedEncodingException | InvalidKeyException exception) {
        exception.printStackTrace();
        return null;
    }
}
```

It is important to note that we should not include any credentials in our codebase. This means that we must save the Mekari API client id and client secret that you obtained from the Mekari Developer dashboard to an environment variable. Modern full-stack frameworks, such as Spring, usually include an application properties file to make managing environment variables easier.

```
MEKARI_API_CLIENT_ID=YOUR_MEKARI_API_CLIENT_ID
MEKARI_API_CLIENT_SECRET=YOUR_MEKARI_CLIENT_SECRET
```

## Wrap It Out

It’s now time to combine everything we’ve learned.

```
import java.nio.charset.StandardCharsets;

public class HmacGeneratorApplication {
    public static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    public static void main(String[] args) {

        OkHttpClient client = new OkHttpClient();

        //      Request Base URL
        String base = "https://api.mekari.com";

        //      HMAC User client id
        String clientId = System.getenv("MEKARI_API_CLIENT_ID");

        //      HMAC User client secret
        String clientSecret = System.getenv("MEKARI_API_CLIENT_SECRET");

        //      Request method GET/POST/PUT/DELETE
        String method = "POST";

        //      Request endpoint
        String path = "/v2/klikpajak/v1/efaktur/out";
        String queryParam = "?auto_approval=false";

        //      Request Body
        String json = "requestBody";

        RequestBody body = RequestBody.create(json, JSON);

        //      Request Date
        String dateFormatted = getDateTimeNowUtcString();

        Request request = new Request.Builder()
            .url(base + path + queryParam)
            .post(body)
            .addHeader("Date", dateFormatted)
            .addHeader("Authorization",
                generateAuthSignature(clientId, clientSecret, method, path + queryParam, dateFormatted)
            )
            .addHeader("Content-Type", "application/json")
            .addHeader("Accept", "application/json")
            .addHeader("x-idempotency-key", UUID.randomUUID().toString())
            .build();

        Call call = client.newCall(request);
        try {
            Response response = call.execute();
            System.out.println(response.body().string());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static String generateAuthSignature(
        String clientId, String clientSecret, String method,
        String pathWithQueryParam, String dateString
    ) {
        String payload = generatePayload(pathWithQueryParam, method, dateString);
        String signature = hmacSha256(clientSecret, payload);

        return "hmac username=\"" + clientId
            + "\", algorithm=\"hmac-sha256\", headers=\"date request-line\", signature=\""
            + signature + "\"";
    }

    private static String generatePayload(String pathWithQueryParam, String method, String dateString) {
        String requestLine = method + ' ' + pathWithQueryParam + " HTTP/1.1";
        return String.join("\n", Arrays.asList("date: " + dateString, requestLine));
    }

    private static String hmacSha256(String clientSecret, String payload) {
        try {
            SecretKeySpec signingKey = new SecretKeySpec(
                clientSecret.getBytes(StandardCharsets.UTF_8), 
                "HmacSHA256"
            );
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(signingKey);

            return Base64.getEncoder()
                .encodeToString(mac.doFinal(payload.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException 
            | UnsupportedEncodingException 
            | InvalidKeyException exception
        ) {
            exception.printStackTrace();
            return null;
        }
    }

    private static String getDateTimeNowUtcString() {
        Instant instant = Instant.now();
        return DateTimeFormatter.ofPattern("EEE, dd MMM yyyy HH:mm:ss O")
            .withZone(ZoneOffset.UTC)
            .withLocale(Locale.US)
            .format(instant);
    }
}
```

If you want to integrate this script with your existing code, you may need to modify it. Additionally, each Mekari API has its own requirements regarding request headers, query, or body, and you may need to change the script based on your needs. We hope that this guide makes integrating Mekari API into your code easier for you.

You can also look at the final code on [this repository](https://github.com/mekari-engineering/mekari-api-hmac-example-java8).

---



---
source: https://developers.mekari.com/docs/kb/product-api
title: Product APIs - Mekari Developers Documentation
---

# Product APIs

Currently we documents the detail of API that we provide for you in Postman Collection. Feel free to explore the APIs details below.

## Talenta

[Postman Collections Talenta API](https://documenter.getpostman.com/view/12246328/UVR5qp6v)

## Klikpajak

[Postman Collections Klikpajak API](https://documenter.getpostman.com/view/17365057/U16hrR5d)

## Qontak OmniChannel

[Qontak Omni Channel API Docs](https://docs.qontak.com/docs/omnichannel-hub/fe286fab4f3cf-qontak-open-api-v1-0-3)

## Qontak CRM

[Postman Collections Qontak CRM API MAG](https://documenter.getpostman.com/view/22728681/2sAXxV6A5V)

## Jurnal API

[Jurnal Api Documentation](https://api-doc.jurnal.id)

## Mekari Expense API

[Mekari Expense API Documentation](https://api-docs.expense.mekari.com)

---



---
source: https://developers.mekari.com/docs/kb/webhooks
title: Webhooks - Mekari Developers Documentation
---

# Webhooks

---

## Table of contents

* [Platform](/docs/kb/webhooks/platform)* [Klikpajak](/docs/kb/webhooks/klikpajak)* [Qontak](/docs/kb/webhooks/qontak)* [Jurnal](/docs/kb/webhooks/jurnal)* [Talenta](/docs/kb/webhooks/talenta)

---



---
source: https://developers.mekari.com/docs/kb/webhooks/platform
title: Platform - Mekari Developers Documentation
---

# Platform

---

## Table of contents

* [Send user logout activity log](/docs/kb/webhooks/platform/platform-authentication-logoff)* [Send user login activity log](/docs/kb/webhooks/platform/platform-authentication-logon)

---



---
source: https://developers.mekari.com/docs/kb/webhooks/platform/platform-authentication-logoff
title: Send user logout activity log - Mekari Developers Documentation
---

# Send user logout activity log

## Prequisite to consume

1. Company request to get their employee activity log through AD-Hoc- SSO will add a flag of `send_webhook_activity_log=true` on the company metadata- Company employee successfully logout on SSO (this will trigger to send to Webhook Service)

## Event

```
platform.authentication.logoff
```

## Schema

```
{
  activity_name: String,
  activity_id: Number,
  auth_protocol: String,
  auth_protocol_id: Number,
  category_name: String,
  category_uid: Number,
  class_name: String,
  class_uid: Number,
  time: String,
  metadata: {
    uid: String,
    product: {
      name: String,
      vendor_name: String,
    },
    version: String,
  },
  severity: String,
  severity_id: Number,
  type_uid: Number,
  type_name: String,
  user: {
    uid: String,
    email_addr: String,
    full_name: String,
    type: String,
    type_id: Number
  },
  timezone_offset: Number,
  status: String,
  status_id: Number,
  status_detail: String,
  is_remote: Boolean,
  is_cleartext: Boolean
}
```

## Example Response

```
{
  "id": 1,
  "user_id": 9611,
  "template_id": 1,
  "created_date": "2023-01-01 00:00:00",
  "updated_date": "2023-01-01 00:00:00",
  "status": 1,
  "last_approval_id": 8002,
  "request_detail": [
    {
      "id": 1,
      "question_id": 1,
      "type": 10,
      "value": "2023-01-01"
    },
    {
      "id": 2,
      "question_id": 2,
      "type": 4,
      "value": "XL"
    },
    {
      "id": 3,
      "question_id": 3,
      "type": 4,
      "value": "Yes"
    },
    {
      "id": 4,
      "question_id": 4,
      "type": 4,
      "value": "Yes"
    },
    {
      "id": 5,
      "question_id": 5,
      "type": 11,
      "value": "Lorem Ipsum"
    }
  ],
  "template": {
    "id": 1,
    "name": "Form Pengajuan Loan",
    "creator": 8002,
    "company_id": 679,
    "category": 3
  },
  "loan": {
    "loan_name_id": 123
  }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/platform/platform-authentication-logon
title: Send user login activity log - Mekari Developers Documentation
---

# Send user login activity log

## Prequisite to consume

1. Company request to get their employee activity log through AD-Hoc- SSO will add a flag of `send_webhook_activity_log=true` on the company metadata- Company employee successfully login to SSO (this will trigger to send to Webhook Service)

## Event

```
platform.authentication.logon
```

## Schema

```
{
  activity_name: String,
  activity_id: Number,
  auth_protocol: String,
  auth_protocol_id: Number,
  category_name: String,
  category_uid: Number,
  class_name: String,
  class_uid: Number,
  time: String,
  metadata: {
    uid: String,
    product: {
      name: String,
      vendor_name: String,
    },
    version: String,
  },
  severity: String,
  severity_id: Number,
  type_uid: Number,
  type_name: String,
  user: {
    uid: String,
    email_addr: String,
    full_name: String,
    type: String,
    type_id: Number
  },
  timezone_offset: Number,
  status: String,
  status_id: Number,
  status_detail: String,
  is_remote: Boolean,
  is_cleartext: Boolean
}
```

## Example Response

```
{
  "id": 1,
  "user_id": 9611,
  "template_id": 1,
  "created_date": "2023-01-01 00:00:00",
  "updated_date": "2023-01-01 00:00:00",
  "status": 1,
  "last_approval_id": 8002,
  "request_detail": [
    {
      "id": 1,
      "question_id": 1,
      "type": 10,
      "value": "2023-01-01"
    },
    {
      "id": 2,
      "question_id": 2,
      "type": 4,
      "value": "XL"
    },
    {
      "id": 3,
      "question_id": 3,
      "type": 4,
      "value": "Yes"
    },
    {
      "id": 4,
      "question_id": 4,
      "type": 4,
      "value": "Yes"
    },
    {
      "id": 5,
      "question_id": 5,
      "type": 11,
      "value": "Lorem Ipsum"
    }
  ],
  "template": {
    "id": 1,
    "name": "Form Pengajuan Loan",
    "creator": 8002,
    "company_id": 679,
    "category": 3
  },
  "loan": {
    "loan_name_id": 123
  }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/klikpajak
title: Klikpajak - Mekari Developers Documentation
---

# Klikpajak

---

## Table of contents

* [Retrieve Output Tax Invoice PDF](/docs/kb/webhooks/klikpajak/klikpajak-efakturpdf-generated)

---



---
source: https://developers.mekari.com/docs/kb/webhooks/klikpajak/klikpajak-efakturpdf-generated
title: Retrieve Output Tax Invoice PDF - Mekari Developers Documentation
---

# Retrieve Output Tax Invoice PDF

Notify users when PDF Link has been created

## Event

```
klikpajak.efakturpdf.generated
```

## Schema

```
{
  "efakturOutPdfLink": String,
  "efakturOutId": Number
}
```

## Example Response

```
{
  "efakturOutPdfLink": "https://jurnal-tax-efaktur-pdf-dev.s3.ap-southeast-1.amazonaws.com/243/2023/APRIL123113231223132-0110002300000002-123113231223132-20230406114753",
  "efakturOutId": 1824
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak
title: Qontak - Mekari Developers Documentation
---

# Qontak

---

## Table of contents

* [Add Deal](/docs/kb/webhooks/qontak/qontak-crm-deal-create)* [Upload Deals](/docs/kb/webhooks/qontak/qontak-crm-deal-upload)* [Edit Deals](/docs/kb/webhooks/qontak/qontak-crm-deal-update)* [Delete Deals](/docs/kb/webhooks/qontak/qontak-crm-deal-delete)* [Add Company](/docs/kb/webhooks/qontak/qontak-crm-company-create)* [Edit Company](/docs/kb/webhooks/qontak/qontak-crm-company-update)* [Delete Company](/docs/kb/webhooks/qontak/qontak-crm-company-delete)* [Add Contact](/docs/kb/webhooks/qontak/qontak-crm-lead-create)* [Edit Contact](/docs/kb/webhooks/qontak/qontak-crm-lead-update)* [Delete Contact](/docs/kb/webhooks/qontak/qontak-crm-lead-delete)* [Create Room](/docs/kb/webhooks/qontak/qontak-chat-room-created)* [Edit Room](/docs/kb/webhooks/qontak/qontak-chat-room-updated)

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-deal-create
title: Add Deal - Mekari Developers Documentation
---

# Add Deal

Create a single Deal

## Prequisite to consume

1. CRM has an object called “DEALS”- Member of organization can add some data on it.- So the trigger is when someone create a new object on table crm\_deals (Deals) it will trigger the webhook with all of information on it

## Event

```
qontak.crm.deal.create
```

## Schema

```
{
  "id": Number,
  "name": String,
  "slug": String,
  "created_at": {"type": String,"format": Date},
  "updated_at": {"type": String,"format": Date},
  "currency": String,
  "size": Number, // or null
  "closed_date": {"type": String,"format": Date},
  "creator_id": Number,
  "creator_name": String,
  "crm_source_id": Number, // or null
  "crm_source_name": null,
  "crm_lost_reason_id": Number, // or null
  "crm_lost_reason_name": null,
  "crm_pipeline_id": Number,
  "crm_pipeline_name": String,
  "crm_stage_id": Number,
  "crm_stage_name": String,
  "start_date": {"type": String,"format": Date},
  "expired_date": {"type": String,"format": Date},
  "crm_priority_id": Number,
  "crm_priority_name": String,
  "crm_company_id": [
    Number, // or null
  ],
  "crm_company_name": [
    String,
  ],
  "crm_lead_ids": [
    Number, // or null
  ],
  "crm_lead_name": [
    String,
  ],
  "product_association_ids": [
    Number, // or null
  ],
  "product_association_name": [
    String,
  ],
  "product_association_quantity": "array",
  "product_association_price": "array",
  "product_association_total_price":"array",
  "additional_fields": [
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String,
    },
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String,
    },
  ]
}
```

## Example Response

```
{
  "id": 1,
  "name": "Deal A",
  "slug": "deal-A-2934",
  "created_at": "2021-07-13T00:00:00.000+07:00",
  "updated_at": "2021-07-13T00:00:00.000+07:00",
  "currency": "IDR",
  "size": "10000000.0",
  "closed_date": "2021-08-15T00:00:00.000+07:00",
  "creator_id": 1,
  "creator_name": "User 1",
  "crm_source_id": null,
  "crm_source_name": null,
  "crm_lost_reason_id": null,
  "crm_lost_reason_name": null,
  "crm_pipeline_id": 1,
  "crm_pipeline_name": "Sales Pipeline",
  "crm_stage_id": 1,
  "crm_stage_name": "Qualified",
  "start_date": "2021-07-13T00:00:00.000+07:00",
  "expired_date": "2022-03-15T00:00:00.000+07:00",
  "crm_priority_id": 1,
  "crm_priority_name": "Priority 1",
  "crm_company_id": [
    1
  ],
  "crm_company_name": [
    "Zoo"
  ],
  "crm_lead_ids": [
    1
  ],
  "crm_lead_name": [
    "Customer Support"
  ],
  "product_association_ids": [
    1
  ],
  "product_association_name": [
    "Special Package"
  ],
  "product_association_quantity": [],
  "product_association_price": [],
  "product_association_total_price": [],
  "additional_fields": [
    {
      "id": 1,
      "name": "additional_field_1",
      "value": null,
      "value_name": "Value Here"
    },
    {
      "id": 2,
      "name": "additional_field_2",
      "value": null,
      "value_name": "Some Value"
    }
  ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-deal-upload
title: Upload Deals - Mekari Developers Documentation
---

# Upload Deals

Create single/multiple deal using upload feature

## Prequisite to consume

1. This webhook actualy same as number 15.- When client upload bunch of deals, that will create new data on crm\_deals it will trigger the webhook with the same json response- On the other hand, in CRM side will restrict the client who can upload- Upload Deals permission = ON

## Event

```
qontak.crm.deal.upload
```

## Schema

```
{
  "id": Number,
  "name": String,
  "slug": String,
  "created_at": {"type": String,"format": Date},
  "updated_at": {"type": String,"format": Date},
  "currency": String,
  "size": Number, // or null
  "closed_date": {"type": String,"format": Date},
  "creator_id": Number,
  "creator_name": String,
  "crm_source_id": Number, // or null
  "crm_source_name": null,
  "crm_lost_reason_id": Number, // or null
  "crm_lost_reason_name": null,
  "crm_pipeline_id": Number,
  "crm_pipeline_name": String,
  "crm_stage_id": Number,
  "crm_stage_name": String,
  "start_date": {"type": String,"format": Date},
  "expired_date": {"type": String,"format": Date},
  "crm_priority_id": Number,
  "crm_priority_name": String,
  "crm_company_id": [
    Number, // or null
  ],
  "crm_company_name": [
    String,
  ],
  "crm_lead_ids": [
    Number, // or null
  ],
  "crm_lead_name": [
    String,
  ],
  "product_association_ids": [
    Number, // or null
  ],
  "product_association_name": [
    String,
  ],
  "product_association_quantity": "array",
  "product_association_price": "array",
  "product_association_total_price":"array",
  "additional_fields": [
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String,
    },
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String,
    },
  ]
}
```

## Example Response

```
{
  "id": 1,
  "name": "Deal A",
  "slug": "deal-A-2934",
  "created_at": "2021-07-13T00:00:00.000+07:00",
  "updated_at": "2021-07-13T00:00:00.000+07:00",
  "currency": "IDR",
  "size": "10000000.0",
  "closed_date": "2021-08-15T00:00:00.000+07:00",
  "creator_id": 1,
  "creator_name": "User 1",
  "crm_source_id": null,
  "crm_source_name": null,
  "crm_lost_reason_id": null,
  "crm_lost_reason_name": null,
  "crm_pipeline_id": 1,
  "crm_pipeline_name": "Sales Pipeline",
  "crm_stage_id": 1,
  "crm_stage_name": "Qualified",
  "start_date": "2021-07-13T00:00:00.000+07:00",
  "expired_date": "2022-03-15T00:00:00.000+07:00",
  "crm_priority_id": 1,
  "crm_priority_name": "Priority 1",
  "crm_company_id": [
    1
  ],
  "crm_company_name": [
    "Zoo"
  ],
  "crm_lead_ids": [
    1
  ],
  "crm_lead_name": [
    "Customer Support"
  ],
  "product_association_ids": [
    1
  ],
  "product_association_name": [
    "Special Package"
  ],
  "product_association_quantity": [],
  "product_association_price": [],
  "product_association_total_price": [],
  "additional_fields": [
    {
      "id": 1,
      "name": "additional_field_1",
      "value": null,
      "value_name": "Value Here"
    },
    {
      "id": 2,
      "name": "additional_field_2",
      "value": null,
      "value_name": "Some Value"
    }
  ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-deal-update
title: Edit Deals - Mekari Developers Documentation
---

# Edit Deals

## Prequisite to consume

1. Client also can edit their deal- When update the data of deal, we will return all of object deal- Which client can edit deals? All client with permission edit deal are Everything

## Event

```
qontak.crm.deal.update
```

## Schema

```
{
  "id": Number,
  "name": String,
  "slug": String,
  "created_at": {"type": String,"format": Date},
  "updated_at": {"type": String,"format": Date},
  "currency": String,
  "size": Number, // or null
  "closed_date": {"type": String,"format": Date},
  "creator_id": Number,
  "creator_name": String,
  "crm_source_id": Number, // or null
  "crm_source_name": null,
  "crm_lost_reason_id": Number, // or null
  "crm_lost_reason_name": null,
  "crm_pipeline_id": Number,
  "crm_pipeline_name": String,
  "crm_stage_id": Number,
  "crm_stage_name": String,
  "start_date": {"type": String,"format": Date},
  "expired_date": {"type": String,"format": Date},
  "crm_priority_id": Number,
  "crm_priority_name": String,
  "crm_company_id": [
    Number, // or null
  ],
  "crm_company_name": [
    String,
  ],
  "crm_lead_ids": [
    Number, // or null
  ],
  "crm_lead_name": [
    String,
  ],
  "product_association_ids": [
    Number, // or null
  ],
  "product_association_name": [
    String,
  ],
  "product_association_quantity": "array",
  "product_association_price": "array",
  "product_association_total_price":"array",
  "additional_fields": [
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String,
    },
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String,
    },
  ]
}
```

## Example Response

```
{
  "id": 1,
  "name": "Deal A",
  "slug": "deal-A-2934",
  "created_at": "2021-07-13T00:00:00.000+07:00",
  "updated_at": "2021-07-13T00:00:00.000+07:00",
  "currency": "IDR",
  "size": "10000000.0",
  "closed_date": "2021-08-15T00:00:00.000+07:00",
  "creator_id": 1,
  "creator_name": "User 1",
  "crm_source_id": null,
  "crm_source_name": null,
  "crm_lost_reason_id": null,
  "crm_lost_reason_name": null,
  "crm_pipeline_id": 1,
  "crm_pipeline_name": "Sales Pipeline",
  "crm_stage_id": 1,
  "crm_stage_name": "Qualified",
  "start_date": "2021-07-13T00:00:00.000+07:00",
  "expired_date": "2022-03-15T00:00:00.000+07:00",
  "crm_priority_id": 1,
  "crm_priority_name": "Priority 1",
  "crm_company_id": [
    1
  ],
  "crm_company_name": [
    "Zoo"
  ],
  "crm_lead_ids": [
    1
  ],
  "crm_lead_name": [
    "Customer Support"
  ],
  "product_association_ids": [
    1
  ],
  "product_association_name": [
    "Special Package"
  ],
  "product_association_quantity": [],
  "product_association_price": [],
  "product_association_total_price": [],
  "additional_fields": [
    {
      "id": 1,
      "name": "additional_field_1",
      "value": null,
      "value_name": "Value Here"
    },
    {
      "id": 2,
      "name": "additional_field_2",
      "value": null,
      "value_name": "Some Value"
    }
  ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-deal-delete
title: Delete Deals - Mekari Developers Documentation
---

# Delete Deals

## Prequisite to consume

1. If client know ID of the deal, it can be delete by hit endpoint delete. or just delete the deal in UI- when Client delete the deal, we will inform client that deal with ID xx is successfully deleted.

## Event

```
qontak.crm.deal.delete
```

## Schema

```
{
  "meta": {
    "status": Number,
    "type": String,
    "error_code": String, //null
    "info": "https://developers.qontak.com/docs/api/response-codes#200",
    "developer_message": String //// inform that data is succesfully deleted
    "message": String,
    "timestamp": Date,
    "log_id": String
  },
 "response" : {
  "id": Number, 
  "name": String,
  "slug": String,
  "external_company_id": Number,
  }
}
```

## Example Response

```
{
  "meta": {
    "status": 200,
    "type": "OK",
    "error_code": null,
    "info": "https://developers.qontak.com/docs/api/response-codes#200",
    "developer_message": "Deal with id 9 successfully deleted",
    "message": "Success",
    "timestamp": "2021-07-20T00:00:00.000+07:00",
    "log_id": "a3aed8a9-5b69-42a0-8718-0015b70456bc"
  },
 "response" : {
  "id": 9, 
  "name": "Deal Astra Januari 2022",
  "slug": "88503b7f-289b-4edc-b185-51670b9cebff",
  "external_company_id":  12332
  }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-company-create
title: Add Company - Mekari Developers Documentation
---

# Add Company

Notify user when new Company is created/added in Qontak CRM

## Event

```
qontak.crm.company.create
```

## Schema

```
 {
  "id": Number,
  "slug": String,
  "name": String,
  "website": String,
  "created_at": {"type": String,"format": Date},
  "updated_at": {"type": String,"format": Date},
  "creator_id": Number,
  "creator_name": String,
  "telephone": String,
  "address": String,
  "country": String,
  "province": String,
  "city": String,
  "zipcode": String,
  "industry_id": Number,
  "industry_name": String,
  "crm_type_id": Number,
  "crm_type_name": String,
  "number_of_employees": Number,
  "crm_source_id": Number,
  "crm_source_name": String,
  "annual_revenue": String,
  "business_reg_number": String,
  "crm_deal_ids": [
    Number  
  ],
  "crm_deal_name": [
    String  
  ],
  "crm_person_ids": [
    Number
  ],
  "crm_person_name": [
    String
  ],
  "ancestry": String,
  "unique_company_id": String,
  "additional_fields": [
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String
    }
  ]
}
```

## Example Response

```
{
  "id": "integer",
  "slug": "string",
  "name": "string",
  "website": "string",
  "created_at": {"type": "string","format": "date-time"},
  "updated_at": {"type": "string","format": "date-time"},
  "creator_id": "integer",
  "creator_name": "string",
  "telephone": "string",
  "address": "string",
  "country": "string",
  "province": "string",
  "city": "string",
  "zipcode": "string",
  "industry_id": "integer",
  "industry_name": "string",
  "crm_type_id": "integer",
  "crm_type_name": "string",
  "number_of_employees": "integer",
  "crm_source_id": "integer",
  "crm_source_name": "string",
  "annual_revenue": "string",
  "business_reg_number": "string",
  "crm_deal_ids": [
    "integer"  
  ],
  "crm_deal_name": [
    "string"  
  ],
  "crm_person_ids": [
    "integer"
  ],
  "crm_person_name": [
    "string"
  ],
  "ancestry": "string",
  "unique_company_id": "string",
  "additional_fields": [
    {
      "id": "integer",
      "name": "string",
      "value": "string",
      "value_name": "string"
    }
  ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-company-update
title: Edit Company - Mekari Developers Documentation
---

# Edit Company

Notify user when Company is updated in Qontak CRM

## Event

```
qontak.crm.company.update
```

## Schema

```
 {
  "id": Number,
  "slug": String,
  "name": String,
  "website": String,
  "created_at": {"type": String,"format": Date},
  "updated_at": {"type": String,"format": Date},
  "creator_id": Number,
  "creator_name": String,
  "telephone": String,
  "address": String,
  "country": String,
  "province": String,
  "city": String,
  "zipcode": String,
  "industry_id": Number,
  "industry_name": String,
  "crm_type_id": Number,
  "crm_type_name": String,
  "number_of_employees": Number,
  "crm_source_id": Number,
  "crm_source_name": String,
  "annual_revenue": String,
  "business_reg_number": String,
  "crm_deal_ids": [
    Number  
  ],
  "crm_deal_name": [
    String  
  ],
  "crm_person_ids": [
    Number
  ],
  "crm_person_name": [
    String
  ],
  "ancestry": String,
  "unique_company_id": String,
  "additional_fields": [
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String
    }
  ]
}
```

## Example Response

```
{
  "id": 38,
  "slug": "78e434ef-61ce-4667-aa4b-ad9f83e6caa3",
  "name": "Company ZianTech",
  "website": "www.ziantech.com",
  "created_at": "2024-01-12T15:56:35.509+07:00",
  "updated_at": "2024-01-12T17:52:25.911+07:00",
  "creator_id": 2,
  "creator_name": "Ade Saputra",
  "telephone": "6221 23323",
  "address": "Jl. Sesama 10",
  "country": "Indonesia",
  "province": "Jawa Tengah",
  "city": "Tegal",
  "zipcode": "",
  "industry_id": 212,
  "industry_name": "Information Technology and Services",
  "crm_type_id": 3,
  "crm_type_name": "Opportunity",
  "number_of_employees": 300,
  "crm_source_id": null,
  "crm_source_name": null,
  "annual_revenue": null,
  "business_reg_number": "",
  "crm_deal_ids": [
    44
  ],
  "crm_deal_name": [
    "Just Deal"
  ],
  "crm_person_ids": [
    8
  ],
  "crm_person_name": [
    "Hendra Karta"
  ],
  "ancestry": "19",
  "unique_company_id": null,
  "additional_fields": [
    {
      "id": 90,
      "name": "daerah",
      "value": "Margasari",
      "value_name": "Margasari"
    }
  ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-company-delete
title: Delete Company - Mekari Developers Documentation
---

# 7. Delete Company

Notify user when Company is deleted from Qontak CRM

## Event

```
qontak.crm.company.delete
```

## Schema

```
{
  "id": Number,
  "name": String,
  "slug": String
}
```

## Example Response

```
{
  "id": 14,
  "name": "PT. CCA engineering",
  "slug": "149c8f2e-a859-4f3d-9a81-5aeeed6bccaf",
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-lead-create
title: Add Contact - Mekari Developers Documentation
---

# Add Contact

Notify user when new Contact is created/added in Qontak CRM

## Event

```
qontak.crm.lead.create
```

## Schema

```
{
  "id": Number,
  "first_name": String,
  "last_name": String,
  "slug": String,
  "created_at": {"type": String,"format": Date},
  "updated_at": {"type": String,"format": Date},
  "job_title": String,
  "creator_id": Number,
  "creator_name": String,
  "creator_username": String,
  "creator_email": String,
  "email": String,
  "telephone": String,
  "crm_status_id": Number,
  "crm_status_name": String,
  "address": String,
  "country": String,
  "province": String,
  "city": String,
  "zipcode": String,
  "date_of_birth": String,
  "crm_source_id": Number,
  "crm_source_name": String,
  "crm_gender_id": Number,
  "crm_gender_name": String,
  "income": String,
  "upload_id": Number,
  "customer_id": String,
  "crm_company_id": Number,
  "crm_company_name": String,
  "crm_deal_ids": [
    Number
  ],
  "crm_deal_name": [
    String
  ],
  "unique_lead_id": String,
  "additional_fields": [
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String
    }
  ],
  "unique_hub_account": String
}
```

## Example Response

```
{
  "id": 33,
  "first_name": "Yahya",
  "last_name": "Zakaria",
  "slug": "25ff75e3-3726-481c-870e-5913fd10a485",
  "created_at": "2024-01-12T18:50:20.474+07:00",
  "updated_at": "2024-01-12T18:50:20.694+07:00",
  "job_title": "COO",
  "creator_id": 1,
  "creator_name": "burhanudin hakim",
  "creator_username": "burhanudin@terbang.com",
  "creator_email": "burhanudin@terbang.com",
  "email": "yahya.zakaria333@gmail.com",
  "telephone": "6283337373222",
  "crm_status_id": 7,
  "crm_status_name": "customer",
  "address": "Jl. Budidaya",
  "country": "Indonesia",
  "province": "Jawa Barat",
  "city": "Bekasi",
  "zipcode": "34930",
  "date_of_birth": null,
  "crm_source_id": 4,
  "crm_source_name": "Iklan",
  "crm_gender_id": null,
  "crm_gender_name": null,
  "income": "",
  "upload_id": null,
  "customer_id": "",
  "crm_company_id": 25,
  "crm_company_name": "PT. ojk engineering",
  "crm_deal_ids": [
    44
  ],
  "crm_deal_name": [
    "Just Deal"
  ],
  "unique_lead_id": null,
  "additional_fields": [
    {
      "id": 91,
      "name": "hobby",
      "value": "Memancing",
      "value_name": "Memancing"
    }
  ],
  "unique_hub_account": null
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-lead-update
title: Edit Contact - Mekari Developers Documentation
---

# Edit Contact

Notify user when Contact is updated in Qontak CRM

## Event

```
qontak.crm.lead.update
```

## Schema

```
{
  "id": Number,
  "first_name": String,
  "last_name": String,
  "slug": String,
  "created_at": {"type": String,"format": Date},
  "updated_at": {"type": String,"format": Date},
  "job_title": String,
  "creator_id": Number,
  "creator_name": String,
  "creator_username": String,
  "creator_email": String,
  "email": String,
  "telephone": String,
  "crm_status_id": Number,
  "crm_status_name": String,
  "address": String,
  "country": String,
  "province": String,
  "city": String,
  "zipcode": String,
  "date_of_birth": String,
  "crm_source_id": Number,
  "crm_source_name": String,
  "crm_gender_id": Number,
  "crm_gender_name": String,
  "income": String,
  "upload_id": Number,
  "customer_id": String,
  "crm_company_id": Number,
  "crm_company_name": String,
  "crm_deal_ids": [
    Number
  ],
  "crm_deal_name": [
    String
  ],
  "unique_lead_id": String,
  "additional_fields": [
    {
      "id": Number,
      "name": String,
      "value": String,
      "value_name": String
    }
  ],
  "unique_hub_account": String
}
```

## Example Response

```
{
  "id": 33,
  "first_name": "Yahyas",
  "last_name": "Zakaria",
  "slug": "25ff75e3-3726-481c-870e-5913fd10a485",
  "created_at": "2024-01-12T18:50:20.474+07:00",
  "updated_at": "2024-01-12T18:52:34.036+07:00",
  "job_title": "COO",
  "creator_id": 1,
  "creator_name": "burhanudin hakim",
  "creator_username": "burhanudin@terbang.com",
  "creator_email": "burhanudin@terbang.com",
  "email": "yahya.zakaria333@gmail.com",
  "telephone": "6283337373222",
  "crm_status_id": 7,
  "crm_status_name": "customer",
  "address": "Jl. Budidaya",
  "country": "Indonesia",
  "province": "Jawa Barat",
  "city": "Bekasi",
  "zipcode": "34930",
  "date_of_birth": null,
  "crm_source_id": 4,
  "crm_source_name": "Iklan",
  "crm_gender_id": null,
  "crm_gender_name": null,
  "income": "",
  "upload_id": null,
  "customer_id": "",
  "crm_company_id": 25,
  "crm_company_name": "PT. ojk engineering",
  "crm_deal_ids": [
    44
  ],
  "crm_deal_name": [
    "Just Deal"
  ],
  "unique_lead_id": null,
  "additional_fields": [
    {
      "id": 91,
      "name": "hobby",
      "value": "Memancing",
      "value_name": "Memancing"
    }
  ],
  "unique_hub_account": null
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-crm-lead-delete
title: Delete Contact - Mekari Developers Documentation
---

# Delete Contact

Notify user when Contact is deleted from Qontak CRM

## Event

```
qontak.crm.lead.delete
```

## Schema

```
{
  "id": Number,
  "name": String,
  "slug": String
}
```

## Example Response

```
{
  "id": 30,
  "name": "Budi Sudarsono",
  "slug": "149c8f2e-a859-4f3d-9a81-5aasdd6bcca8",
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-chat-room-created
title: Create Room - Mekari Developers Documentation
---

# Create Room

Webhook when room created

## Event

```
qontak.chat.room.created
```

## Schema

```
{
  "id": String,
  "name": String,
  "description": "",
  "status": String,
  "type": String,
  "tags": [],
  "channel": String,
  "channel_account": String,
  "organization_id": String,
  "account_uniq_id": "6282271511514",
  "channel_integration_id": String,
  "session_at": Date,
  "last_message": {
    "id": String,
    "type": String,
    "room_id": String,
    "is_campaign": Boolean,
    "sender_id": String,
    "sender_type": String,
    "participant_id": String,
    "participant_type": String,
    "organization_id": String,
    "text": String,
    "status": String,
    "channel": String,
    "raw_message": {
      "contacts": [
        {
          "wa_id": String,
          "profile": {
            "name": String
          }
        }
      ],
      "messages": [
        {
          "id": String,
          "from": String,
          "text": {
            "body": String
          },
          "type": String,
          "timestamp": String
        }
      ],
      "metadata": {
        "phone_number_id": String,
        "display_phone_number": String
      },
      "messaging_product": String
    },
    "external_id": String,
    "local_id": null,
    "created_at": Date
  },
  "unread_count": Number,
  "created_at": Date,
  "last_message_at": Date,
  "last_activity_at": Date,
  "updated_at": Date,
  "avatar": {
    "url": String,
    "large": {
      "url": String
    },
    "filename": null,
    "size": Number,
    "small": {
      "url": String
    },
    "medium": {
      "url": String
    }
  },
  "note": null,
  "resolved_at": null,
  "external_id": "",
  "resolved_by_id": null,
  "resolved_by_type": null,
  "extra": {
    "is_participant_online": Boolean
  },
  "agent_ids": [],
  "is_dont_auto_resolve": Boolean,
  "email_cc": null,
  "is_unresponded": Boolean,
  "is_manual_survey": Boolean,
  "data_event": String
}
```

## Example Response

```
{
  "id": "5113b80b-fa7d-4a50-9590-1dfd55325580",
  "name": "adrian",
  "description": "",
  "status": "unassigned",
  "type": "Models::CustomerServiceRoom",
  "tags": [],
  "channel": "wa_cloud",
  "channel_account": "Sandbox Qontak 6",
  "organization_id": "859438e6-10ac-48ac-8d8c-d9d20bba8382",
  "account_uniq_id": "6282271511514",
  "channel_integration_id": "fa914ed7-672d-4530-97bd-1c554ab2e1ee",
  "session_at": "2024-05-15T16:36:04.000Z",
  "last_message": {
    "id": "a667db6f-6b67-4320-bfc2-b098f4ed2e2a",
    "type": "text",
    "room_id": "5113b80b-fa7d-4a50-9590-1dfd55325580",
    "is_campaign": false,
    "sender_id": "5f43e133-866c-4e5f-aaf1-3b92ccec0ee4",
    "sender_type": "Models::Contact",
    "participant_id": "1f345792-fe27-422c-9fa5-e54afe12d406",
    "participant_type": "customer",
    "organization_id": "859438e6-10ac-48ac-8d8c-d9d20bba8382",
    "text": "asdasd",
    "status": "created",
    "channel": "wa_cloud",
    "raw_message": {
      "contacts": [
        {
          "wa_id": "6282271511514",
          "profile": {
            "name": "Adrian Rahmandanu"
          }
        }
      ],
      "messages": [
        {
          "id": "wamid.HBgNNjI4MjI3MTUxMTUxNBUCABIYFDNBRjFBN0UxRUIyOTE2Q0IxRDg2AA==",
          "from": "6282271511514",
          "text": {
            "body": "asdasd"
          },
          "type": "text",
          "timestamp": "1715790964"
        }
      ],
      "metadata": {
        "phone_number_id": "540083594083559",
        "display_phone_number": "6289618625602"
      },
      "messaging_product": "whatsapp"
    },
    "external_id": "wamid.HBgNNjI4MjI3MTUxMTUxNBUCABIYFDNBRjFBN0UxRUIyOTE2Q0IxRDg2AA==",
    "local_id": null,
    "created_at": "2024-05-15T16:36:04.000Z"
  },
  "unread_count": 1,
  "created_at": "2024-05-15T16:36:05.675Z",
  "last_message_at": "2024-05-15T16:36:04.000Z",
  "last_activity_at": "2024-05-15T16:36:04.000Z",
  "updated_at": "2024-05-15T16:36:05.702Z",
  "avatar": {
    "url": "https://qontak-hub-production.s3-ap-southeast-1.amazonaws.com/assets/qi-user.png",
    "large": {
      "url": "https://qontak-hub-production.s3-ap-southeast-1.amazonaws.com/assets/qi-user.png"
    },
    "filename": null,
    "size": 0,
    "small": {
      "url": "https://qontak-hub-production.s3-ap-southeast-1.amazonaws.com/assets/qi-user.png"
    },
    "medium": {
      "url": "https://qontak-hub-production.s3-ap-southeast-1.amazonaws.com/assets/qi-user.png"
    }
  },
  "note": null,
  "resolved_at": null,
  "external_id": "",
  "resolved_by_id": null,
  "resolved_by_type": null,
  "extra": {
    "is_participant_online": false
  },
  "agent_ids": [],
  "is_dont_auto_resolve": false,
  "email_cc": null,
  "is_unresponded": true,
  "is_manual_survey": false,
  "data_event": "room_created"
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/qontak/qontak-chat-room-updated
title: Edit Room - Mekari Developers Documentation
---

# Edit Room

## Prequisite to consume

1. webhook when there is changes on room status
   * assigned* resolved- webhook that triggered when there is changes inside room status

## Event

```
qontak.chat.room.updated
```

## Schema

```
{
  "id": String,
  "name": String,
  "description": String,
  "status": String,
  "type": String,
  "tags": [],
  "channel": String,
  "channel_account": String,
  "organization_id": String,
  "account_uniq_id": String,
  "channel_integration_id": String,
  "session_at": Date,
  "last_message": {
    "id": String,
    "type": String,
    "room_id": String,
    "is_campaign": Boolean,
    "sender_id": String,
    "sender_type": String,
    "participant_id": String,
    "participant_type": String,
    "organization_id": String,
    "text": String,
    "status": String,
    "channel": String,
    "raw_message": {
      "contacts": [
        {
          "wa_id": String,
          "profile": {
            "name": String
          }
        }
      ],
      "messages": [
        {
          "id": String,
          "from": String,
          "text": {
            "body": String
          },
          "type": String,
          "timestamp": String
        }
      ],
      "metadata": {
        "phone_number_id": String,
        "display_phone_number": String
      },
      "messaging_product": String
    },
    "external_id": String,
    "local_id": null,
    "created_at": Date
  },
  "unread_count": Number,
  "created_at": String,
  "last_message_at": Date,
  "last_activity_at": Date,
  "updated_at": Date,
  "avatar": {
    "url": String,
    "large": {
      "url": String
    },
    "filename": null,
    "size": Number,
    "small": {
      "url": String
    },
    "medium": {
      "url": String
    }
  },
  "note": null,
  "resolved_at": null,
  "external_id": "",
  "resolved_by_id": null,
  "resolved_by_type": null,
  "extra": {
    "is_participant_online": Boolean
  },
  "agent_ids": [],
  "is_dont_auto_resolve": Boolean,
  "email_cc": null,
  "is_unresponded": Boolean,
  "is_manual_survey": Boolean,
  "data_event": String
}
```

## Example Response

```
{
  "id": "5113b80b-fa7d-4a50-9590-1dfd55325580",
  "name": "adrian",
  "description": "",
  "status": "unassigned",
  "type": "Models::CustomerServiceRoom",
  "tags": [],
  "channel": "wa_cloud",
  "channel_account": "Sandbox Qontak 6",
  "organization_id": "859438e6-10ac-48ac-8d8c-d9d20bba8382",
  "account_uniq_id": "6282271511514",
  "channel_integration_id": "fa914ed7-672d-4530-97bd-1c554ab2e1ee",
  "session_at": "2024-05-15T16:36:04.000Z",
  "last_message": {
    "id": "a667db6f-6b67-4320-bfc2-b098f4ed2e2a",
    "type": "text",
    "room_id": "5113b80b-fa7d-4a50-9590-1dfd55325580",
    "is_campaign": false,
    "sender_id": "5f43e133-866c-4e5f-aaf1-3b92ccec0ee4",
    "sender_type": "Models::Contact",
    "participant_id": "1f345792-fe27-422c-9fa5-e54afe12d406",
    "participant_type": "customer",
    "organization_id": "859438e6-10ac-48ac-8d8c-d9d20bba8382",
    "text": "asdasd",
    "status": "created",
    "channel": "wa_cloud",
    "raw_message": {
      "contacts": [
        {
          "wa_id": "6282271511514",
          "profile": {
            "name": "Adrian Rahmandanu"
          }
        }
      ],
      "messages": [
        {
          "id": "wamid.HBgNNjI4MjI3MTUxMTUxNBUCABIYFDNBRjFBN0UxRUIyOTE2Q0IxRDg2AA==",
          "from": "6282271511514",
          "text": {
            "body": "asdasd"
          },
          "type": "text",
          "timestamp": "1715790964"
        }
      ],
      "metadata": {
        "phone_number_id": "540083594083559",
        "display_phone_number": "6289618625602"
      },
      "messaging_product": "whatsapp"
    },
    "external_id": "wamid.HBgNNjI4MjI3MTUxMTUxNBUCABIYFDNBRjFBN0UxRUIyOTE2Q0IxRDg2AA==",
    "local_id": null,
    "created_at": "2024-05-15T16:36:04.000Z"
  },
  "unread_count": 1,
  "created_at": "2024-05-15T16:36:05.675Z",
  "last_message_at": "2024-05-15T16:36:04.000Z",
  "last_activity_at": "2024-05-15T16:36:04.000Z",
  "updated_at": "2024-05-15T16:36:05.702Z",
  "avatar": {
    "url": "https://qontak-hub-production.s3-ap-southeast-1.amazonaws.com/assets/qi-user.png",
    "large": {
      "url": "https://qontak-hub-production.s3-ap-southeast-1.amazonaws.com/assets/qi-user.png"
    },
    "filename": null,
    "size": 0,
    "small": {
      "url": "https://qontak-hub-production.s3-ap-southeast-1.amazonaws.com/assets/qi-user.png"
    },
    "medium": {
      "url": "https://qontak-hub-production.s3-ap-southeast-1.amazonaws.com/assets/qi-user.png"
    }
  },
  "note": null,
  "resolved_at": null,
  "external_id": "",
  "resolved_by_id": null,
  "resolved_by_type": null,
  "extra": {
    "is_participant_online": false
  },
  "agent_ids": [],
  "is_dont_auto_resolve": false,
  "email_cc": null,
  "is_unresponded": true,
  "is_manual_survey": false,
  "data_event": "add_agent"
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/jurnal
title: Jurnal - Mekari Developers Documentation
---

# Jurnal

---

## Table of contents

* [Send Person or Contact](/docs/kb/webhooks/jurnal/send-contact)* [Send Receive Payment](/docs/kb/webhooks/jurnal/send-receive-payment)* [Send Sales Invoice](/docs/kb/webhooks/jurnal/send-sales-invoice)* [Send Sales Order](/docs/kb/webhooks/jurnal/send-sales-order)* [Send Sales Quote](/docs/kb/webhooks/jurnal/send-sales-quote)

---



---
source: https://developers.mekari.com/docs/kb/webhooks/jurnal/send-contact
title: Send Person or Contact - Mekari Developers Documentation
---

# Send Person or Contact to Webhook Consumer Every New Contact Created

## Prequisite to Consume

1. Feature contact webhook for that company is active in [Jurnal](https://jurnal.id)- User need to create new contact

## Event

```
jurnal.person.created
```

## Schema

```
{
  "id": "integer",
  "display_name": "string",
  "title": "string",
  "first_name": "string",
  "middle_name": "string",
  "last_name": "string",
  "fullname_with_title": "string",
  "mobile": "string",
  "identity_type": "string",
  "identity_number": "string",
  "email": "string",
  "other_detail": "string",
  "associate_company": "string",
  "phone": "string",
  "fax": "string",
  "tax_no": "string",
  "archive": "string",
  "billing_address": "string",
  "billing_address_no": "string",
  "billing_address_rt": "string",
  "billing_address_rw": "string",
  "billing_address_post_code": "string",
  "billing_address_kelurahan": "string",
  "billing_address_kecamatan": "string",
  "billing_address_kabupaten": "string",
  "billing_address_provinsi": "string",
  "address": "string",
  "bank_account_details": [
    {
      "bank_name": "string",
      "bank_partner_id": "integer",
      "bank_branch": "string",
      "bank_account_holder_name": "string",
      "bank_account_number": "string",
      "is_valid": "boolean"
    }
  ],
  "default_ar_account_id": "integer",
  "default_ap_account_id": "integer",
  "disable_max_credit_limit": "boolean",
  "disable_max_debit_limit": "boolean",
  "max_credit_limit": "integer",
  "max_debit_limit": "integer",
  "term_id": "integer",
  "is_customer": "boolean",
  "is_vendor": "boolean",
  "is_employee": "boolean",
  "custom_id": "integer",
  "source": "apikey",
  "is_others": "boolean"
}
```

## Example Response

```
{
    "id": 834496,
    "display_name": "Bambang",
    "title": null,
    "first_name": null,
    "middle_name": null,
    "last_name": null,
    "fullname_with_title": "",
    "mobile": null,
    "identity_type": "",
    "identity_number": null,
    "email": "",
    "other_detail": null,
    "associate_company": null,
    "phone": null,
    "fax": null,
    "tax_no": null,
    "archive": false,
    "billing_address": null,
    "billing_address_no": "",
    "billing_address_rt": "",
    "billing_address_rw": "",
    "billing_address_post_code": "",
    "billing_address_kelurahan": "",
    "billing_address_kecamatan": "",
    "billing_address_kabupaten": "",
    "billing_address_provinsi": "",
    "address": null,
    "bank_account_details": [
      {
        "bank_name": null,
        "bank_partner_id": 0,
        "bank_branch": "",
        "bank_account_holder_name": "",
        "bank_account_number": "",
        "is_valid": null
      }
    ],
    "default_ar_account_id": 30918189,
    "default_ap_account_id": 30918196,
    "disable_max_credit_limit": true,
    "disable_max_debit_limit": true,
    "max_credit_limit": null,
    "max_debit_limit": null,
    "term_id": null,
    "is_customer": true,
    "is_vendor": false,
    "is_employee": false,
    "custom_id": null,
    "source": "apikey",
    "is_others": false
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/jurnal/send-receive-payment
title: Send Receive Payment - Mekari Developers Documentation
---

# Send Receive Payment to Webhook Consumer Every New Receive Payment Created

## Prequisite to Consume

1. Feature receive payment webhook for that company is active in [Jurnal](https://jurnal.id)- User need to create new receive payment

## Event

```
jurnal.receivepayment.created
```

## Schema

```
{
  "id": "integer",
  "transaction_no": "string",
  "token": "string",
  "memo": "string",
  "source": "string",
  "custom_id": "integer",
  "status": "string",
  "transaction_status": {
    "id": "integer",
    "name": "Paid",
    "created_at": {"type": "string","format": "date-time"},,
    "updated_at": {"type": "string","format": "date-time"},,
    "name_bahasa": "string"
  },
  "deleted_at": {"type": "string","format": "date-time"},,
  "audited_by": "string",
  "transaction_date": {"type": "string","format": "date-time"},,
  "due_date": {"type": "string","format": "date-time"},,
  "person": {
    "id": "integer",
    "name": "string",
    "email": "string",
    "address": "string",
    "phone": "string",
    "fax": "string"
  },
  "transaction_type": {
    "id": "integer",
    "name": "string"
  },
  "payment_method": {
    "id": "integer",
    "name": "string"
  },
  "deposit_to": {
    "id": "integer",
    "name": "string",
    "number": "string",
    "category": {
      "id": "integer",
      "name": "string"
    }
  },
  "is_draft": "boolean",
  "proforma_id": "integer",
  "witholding": {
    "witholding_account_name": "string",
    "witholding_account_number": "integer",
    "account_id": "integer",
    "value": "string",
    "type": "string",
    "amount": "integer",
    "amount_currency_format": "string",
    "category": {
      "id": "integer",
      "name": "string"
    }
  },
  "original_amount": "integer",
  "original_amount_currency_format": "string",
  "total": "integer",
  "total_currency_format": "string",
  "records": [
    {
      "id": "integer",
      "transaction_id": "integer",
      "amount": "string",
      "description": "string",
      "transaction_type_id": "integer",
      "transaction_type": "string",
      "transaction_no": "string",
      "amount_currency_format": "string",
      "transaction_due_date": {"type": "string","format": "date-time"},
      "transaction_total": "integer",
      "transaction_total_currency_format": "string",
      "transaction_balance_due": "integer",
      "transaction_balance_due_currency_format": "string"
    }
  ],
  "is_reconciled": "boolean",
  "is_create_before_conversion": "boolean",
  "is_import": "boolean",
  "import_id": "integer",
  "attachments": "array",
  "tags": "array",
  "tags_string": "",
  "created_at": {"type": "string","format": "date-time"},
  "updated_at": {"type": "string","format": "date-time"},
  "currency_code": "IDR",
  "currency_list_id": "integer",
  "currency_from_id": "integer",
  "currency_to_id": "integer",
  "multi_currency_id": "integer",
  "currency_rate": "integer",
  "comments_size": "integer"
}
```

## Example Response

```
{
    "id": 4455095,
    "transaction_no": "10346",
    "token": "-bAyCSXEt3tkC2gtQEhpPw",
    "memo": "",
    "source": null,
    "custom_id": null,
    "status": "approved",
    "transaction_status": {
      "id": 3,
      "name": "Paid",
      "created_at": "2014-11-09T05:44:30.000Z",
      "updated_at": "2014-11-09T05:44:30.000Z",
      "name_bahasa": "Lunas"
    },
    "deleted_at": null,
    "audited_by": null,
    "transaction_date": "30/01/2024",
    "due_date": null,
    "person": {
      "id": 798833,
      "name": "Awan",
      "email": "rosa@gmail.com",
      "address": null,
      "phone": null,
      "fax": null
    },
    "transaction_type": {
      "id": 2,
      "name": "Receive Payment"
    },
    "payment_method": {
      "id": 1193180,
      "name": "Cash"
    },
    "deposit_to": {
      "id": 30918104,
      "name": "Cash",
      "number": "1-10001",
      "category": {
        "id": 3,
        "name": "Cash & Bank"
      }
    },
    "is_draft": false,
    "proforma_id": 2886,
    "witholding": {
      "witholding_account_name": null,
      "witholding_account_number": null,
      "account_id": null,
      "value": "0.0",
      "type": "value",
      "amount": 0,
      "amount_currency_format": "Rp.  0,00",
      "category": {
        "id": null,
        "name": null
      }
    },
    "original_amount": 10000,
    "original_amount_currency_format": "Rp.  10.000,00",
    "total": 10000,
    "total_currency_format": "Rp.  10.000,00",
    "records": [
      {
        "id": 1023667,
        "transaction_id": 4455094,
        "amount": "10000.0",
        "description": "",
        "transaction_type_id": 1,
        "transaction_type": "Sales Invoice",
        "transaction_no": "10242",
        "amount_currency_format": "Rp.  10.000,00",
        "transaction_due_date": "14/02/2024",
        "transaction_total": 10000,
        "transaction_total_currency_format": "Rp.  10.000,00",
        "transaction_balance_due": 10000,
        "transaction_balance_due_currency_format": "Rp.  10.000,00"
      }
    ],
    "is_reconciled": false,
    "is_create_before_conversion": null,
    "is_import": false,
    "import_id": null,
    "attachments": [],
    "tags": null,
    "tags_string": "",
    "created_at": "2024-01-30T11:17:53.000Z",
    "updated_at": "2024-01-30T11:17:53.000Z",
    "currency_code": "IDR",
    "currency_list_id": 8438,
    "currency_from_id": 1,
    "currency_to_id": 1,
    "multi_currency_id": 133378,
    "currency_rate": 1,
    "comments_size": 0
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/jurnal/send-sales-invoice
title: Send Sales Invoice - Mekari Developers Documentation
---

# Send Sales Invoice to Webhook Consumer Every New Sales Invoice Created

## Prequisite to Consume

1. Feature sales invoice webhook for that company is active in [Jurnal](https://jurnal.id)- User need to create new sales invoice

## Event

```
jurnal.salesinvoice.created
```

## Schema

```
{
  "kind": "string",
  "id": "integer",
  "transaction_no": "string",
  "selected_po_id": "integer",
  "selected_pq_id": "integer",
  "token": "string",
  "email": "string",
  "source": "string",
  "address": "string",
  "message": "string",
  "memo": "string",
  "remaining": "string",
  "original_amount": "string",
  "shipping_price": "string",
  "shipping_address": "string",
  "is_shipped": "boolean",
  "ship_via": "string",
  "reference_no": "string",
  "tracking_no": "string",
  "tax_after_discount": "boolean",
  "tax_amount": "string",
  "witholding_value": "string",
  "status": "string",
  "discount_price": "string",
  "witholding_type": "string",
  "amount_receive": "string",
  "subtotal": "string",
  "deposit": "string",
  "custom_id": "string",
  "created_at": {"type": "string","format": "date-time"},
  "deleted_at": {"type": "string","format": "date-time"},,
  "audited_by": "string",
  "transaction_date": {"type": "string","format": "date-time"},
  "due_date": {"type": "string","format": "date-time"},
  "shipping_date": {"type": "string","format": "date"},
  "witholding_amount": "integer",
  "witholding_amount_currency_format": "string",
  "discount_per_lines": "string",
  "discount_per_lines_currency_format": "string",
  "payment_received_amount": "string",
  "payment_received_amount_currency_format": "string",
  "remaining_currency_format": "string",
  "original_amount_currency_format": "string",
  "shipping_price_currency_format": "string",
  "tax_amount_currency_format": "string",
  "discount_price_currency_format": "string",
  "amount_receive_currency_format": "string",
  "subtotal_currency_format": "string",
  "deposit_currency_format": "string",
  "has_deliveries": "boolean",
  "is_create_before_conversion": "boolean",
  "is_import": "boolean",
  "import_id": "integer",
  "has_credit_memos": "boolean",
  "credit_memo_balance": "integer",
  "credit_memo_balance_currency_format": "string",
  "transaction_status": {
    "id": "integer",
    "name": "string",
    "name_bahasa": "string"
  },
  "transaction_lines_attributes": [
    {
      "id": "integer",
      "custom_id": "string",
      "description": "string",
      "amount": "string",
      "discount": "string",
      "rate": "string",
      "tax": "string",
      "line_tax": {
        "id": "integer",
        "name": "string",
        "rate": "string",
        "children": "array"
      },
      "amount_currency_format": "string",
      "rate_currency_format": "string",
      "has_return_line": "boolean",
      "quantity": "double",
      "sell_acc_id": "integer",
      "buy_acc_id": "integer",
      "product": {
        "id": "integer",
        "name": "string",
        "code": "string",
        "product_custom_id": "string",
        "archive": "boolean",
        "quantity": "double",
        "quantity_string": "string",
        "track_inventory": "boolean",
        "sell_price_per_unit": "string",
        "buy_price_per_unit": "string",
        "link": "string"
      },
      "unit": {
        "id": "integer",
        "name": "string"
      },
      "units": "array",
      "pricing_rule": "array"
    }
  ],
  "payments": "array",
  "sales_returns": "array",
  "sales_deliveries": "array",
  "credit_memos": "array",
  "sales_quote": {
    "id": "integer",
    "transaction_no": "string"
  },
  "person": {
    "id": "integer",
    "display_name": "string",
    "title": "string",
    "first_name": "string",
    "middle_name": "string",
    "last_name": "string",
    "tax_no": "string",
    "email": "string",
    "address": "string",
    "billing_address": "string",
    "phone": "string",
    "fax": "string"
  },
  "discount_type": {
    "id": "integer",
    "name": "string",
    "name_bahasa": "string"
  },
  "discount_unit": "string",
  "warehouse": {
    "id": "integer",
    "name": "string",
    "code": "string",
    "status": "string"
  },
  "deposit_to": {
    "id": "integer",
    "name": "string",
    "number": "integer",
    "category": {
      "id": "integer",
      "name": "string"
    }
  },
  "term": {
    "id": "integer",
    "name": "string",
    "longetivity": "integer"
  },
  "tags": [
    {
      "id": "integer",
      "name": "string"
    },
    {
      "id": "integer",
      "name": "string"
    }
  ],
  "tags_string":"string",
  "has_payments": "boolean",
  "earliest_payment_date": {"type": "string","format": "date-time"},
  "tax": {
    "id": "integer",
    "name": "string",
    "rate": "string"
  },
  "tax_details": [
    {
      "name": "string",
      "tax_amount": "double",
      "tax_amount_currency_format": "string"
    }
  ],
  "use_tax_inclusive": "boolean",
  "attachments": "array",
  "email_previews": {
    "times_sent": "integer",
    "sent_to_list": "array"
  },
  "is_reconciled": "boolean",
  "witholding_account": {
    "id": "integer",
    "name": "string",
    "number": "integer",
    "category": {
      "id": "integer",
      "name": "string"
    }
  },
  "updated_at": {"type": "string","format": "date-time"},
  "currency_code": "IDR",
  "currency_list_id": "integer",
  "currency_from_id": "integer",
  "currency_to_id": "integer",
  "multi_currency_id": "integer",
  "currency_rate": "integer",
  "sales_withholdings": "array"
}
```

## Example Response

```
{
    "kind": "Sales Invoice",
    "id": 4455096,
    "transaction_no": "10243",
    "selected_po_id": null,
    "selected_pq_id": null,
    "token": "ZzXVK1zgE3kEE7VF5MiCPA",
    "email": "morgan@gmail.com, fadzil@gmail.com",
    "source": "v3/revamp",
    "address": "Jl. jalan ke sumedank",
    "message": "Test Default msg",
    "memo": "",
    "remaining": "10000.0",
    "original_amount": "10000.0",
    "shipping_price": "0.0",
    "shipping_address": null,
    "is_shipped": false,
    "ship_via": "",
    "reference_no": "",
    "tracking_no": "",
    "tax_after_discount": true,
    "tax_amount": "0.0",
    "witholding_value": "0.0",
    "status": "approved",
    "discount_price": "0.0",
    "witholding_type": "value",
    "amount_receive": "0.0",
    "subtotal": "10000.0",
    "deposit": "0.0",
    "custom_id": null,
    "created_at": "2024-01-30T11:18:28.000Z",
    "deleted_at": null,
    "audited_by": null,
    "transaction_date": "30/01/2024",
    "due_date": "30/03/2024",
    "shipping_date": null,
    "witholding_amount": 0,
    "witholding_amount_currency_format": "Rp.  0,00",
    "discount_per_lines": "0.0",
    "discount_per_lines_currency_format": "Rp.  0,00",
    "payment_received_amount": "0.0",
    "payment_received_amount_currency_format": "Rp.  0,00",
    "remaining_currency_format": "Rp.  10.000,00",
    "original_amount_currency_format": "Rp.  10.000,00",
    "shipping_price_currency_format": "Rp.  0,00",
    "tax_amount_currency_format": "Rp.  0,00",
    "discount_price_currency_format": "Rp.  0,00",
    "amount_receive_currency_format": "Rp.  0,00",
    "subtotal_currency_format": "Rp.  10.000,00",
    "deposit_currency_format": "Rp.  0,00",
    "has_deliveries": false,
    "is_create_before_conversion": null,
    "is_import": false,
    "import_id": null,
    "has_credit_memos": false,
    "credit_memo_balance": 0,
    "credit_memo_balance_currency_format": "Rp.  0,00",
    "transaction_status": {
      "id": 1,
      "name": "Open",
      "name_bahasa": "Belum Dibayar"
    },
    "transaction_lines_attributes": [
      {
        "id": 4670184,
        "custom_id": null,
        "description": "",
        "amount": "10000.0",
        "discount": "0.0",
        "rate": "10000.0",
        "tax": null,
        "line_tax": {
          "id": null,
          "name": null,
          "rate": null,
          "children": []
        },
        "amount_currency_format": "Rp.  10.000,00",
        "rate_currency_format": "Rp.  10.000,00",
        "has_return_line": false,
        "quantity": 1,
        "sell_acc_id": 30918337,
        "buy_acc_id": 30918340,
        "product": {
          "id": 14523140,
          "name": "A1 Morgan Ganteng",
          "code": null,
          "product_custom_id": null,
          "archive": false,
          "quantity": 0,
          "quantity_string": "0.0",
          "track_inventory": false,
          "sell_price_per_unit": "10000.0",
          "buy_price_per_unit": "0.0",
          "link": null
        },
        "unit": {
          "id": 83000,
          "name": "Buah"
        },
        "units": [],
        "pricing_rule": null
      }
    ],
    "payments": [],
    "sales_returns": [],
    "sales_deliveries": [],
    "credit_memos": [],
    "sales_quote": {
      "id": null,
      "transaction_no": null
    },
    "person": {
      "id": 717245,
      "display_name": "alicloudSRS",
      "title": null,
      "first_name": "",
      "middle_name": "",
      "last_name": "",
      "tax_no": "",
      "email": "morgan@gmail.com, fadzil@gmail.com",
      "address": "Jl. jalan ke Dufan",
      "billing_address": "Jl. jalan ke sumedank",
      "phone": "0895355293048",
      "fax": ""
    },
    "discount_type": {
      "id": 1,
      "name": "Percent",
      "name_bahasa": "Persen"
    },
    "discount_unit": "0.0",
    "warehouse": {
      "id": null,
      "name": null,
      "code": null,
      "status": null
    },
    "deposit_to": {
      "id": null,
      "name": null,
      "number": null,
      "category": {
        "id": null,
        "name": null
      }
    },
    "term": {
      "id": 296675,
      "name": "Net 60",
      "longetivity": 60
    },
    "tags": null,
    "tags_string": "",
    "has_payments": false,
    "earliest_payment_date": "",
    "tax": {
      "id": null,
      "name": null,
      "rate": null
    },
    "tax_details": [],
    "use_tax_inclusive": false,
    "attachments": [],
    "email_previews": {
      "times_sent": 0,
      "sent_to_list": []
    },
    "is_reconciled": false,
    "witholding_account": {
      "id": null,
      "name": null,
      "number": null,
      "category": {
        "id": null,
        "name": null
      }
    },
    "updated_at": "2024-01-30T11:18:28.000Z",
    "currency_code": "IDR",
    "currency_list_id": 8438,
    "currency_from_id": 1,
    "currency_to_id": 1,
    "multi_currency_id": 133379,
    "currency_rate": 1,
    "sales_withholdings": []
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/jurnal/send-sales-order
title: Send Sales Order - Mekari Developers Documentation
---

# Send Sales Order to Webhook Consumer Every New Sales Order Created

## Prequisite to Consume

1. Feature sales order webhook for that company is active in [Jurnal](https://jurnal.id)- User need to create new sales order

## Event

```
jurnal.salesorder.created
```

## Schema

```
{
  "kind": "string",
  "id": "integer",
  "transaction_no": "string",
  "selected_po_id": "integer",
  "token": "string",
  "email": "string",
  "source": "string",
  "address": "string",
  "message": "string",
  "memo": "string",
  "remaining": "string",
  "original_amount": "string",
  "shipping_price": "string",
  "shipping_address": "string",
  "is_shipped": "boolean",
  "ship_via": "string",
  "reference_no": "string",
  "tracking_no": "string",
  "tax_after_discount": "boolean",
  "tax_amount": "string",
  "status": "string",
  "discount_price": "string",
  "amount_receive": "string",
  "subtotal": "string",
  "deposit": "string",
  "custom_id": "string",
  "created_at": {"type": "string","format": "date-time"},
  "deleted_at": {"type": "string","format": "date-time"},,
  "transaction_date": {"type": "string","format": "date-time"},
  "due_date": {"type": "string","format": "date-time"},
  "shipping_date": {"type": "string","format": "date"},
  "discount_per_lines": "string",
  "discount_per_lines_currency_format": "string",
  "payment_received_amount": "string",
  "payment_received_amount_currency_format": "string",
  "remaining_currency_format": "string",
  "original_amount_currency_format": "string",
  "shipping_price_currency_format": "string",
  "tax_amount_currency_format": "string",
  "discount_price_currency_format": "string",
  "amount_receive_currency_format": "string",
  "subtotal_currency_format": "string",
  "deposit_currency_format": "string",
  "has_deliveries": "boolean",
  "is_create_before_conversion": "boolean",
  "is_import": "boolean",
  "import_id": "integer",
  "has_credit_memos": "boolean",
  "credit_memo_balance": "integer",
  "credit_memo_balance_currency_format": "string",
  "transaction_status": {
    "id": "integer",
    "name": "string",
    "name_bahasa": "string"
  },
  "transaction_lines_attributes": [
    {
      "id": "integer",
      "custom_id": "string",
      "description": "string",
      "amount": "string",
      "discount": "string",
      "rate": "string",
      "tax": "string",
      "line_tax": {
        "id": "integer",
        "name": "string",
        "rate": "string",
        "children": "array"
      },
      "amount_currency_format": "string",
      "rate_currency_format": "string",
      "has_return_line": "boolean",
      "quantity": "double",
      "sell_acc_id": "integer",
      "buy_acc_id": "integer",
      "product": {
        "id": "integer",
        "name": "string",
        "code": "string",
        "product_custom_id": "string",
        "archive": "boolean",
        "quantity": "double",
        "quantity_string": "string",
        "track_inventory": "boolean",
        "sell_price_per_unit": "string",
        "buy_price_per_unit": "string",
        "link": "string"
      },
      "unit": {
        "id": "integer",
        "name": "string"
      },
      "units": "array",
      "pricing_rule": "array",
      "remaining_quantity": "integer"
    }
  ],
  "payments": "array",
  "sales_returns": "array",
  "sales_deliveries": "array",
  "credit_memos": "array",
  "sales_quote": {
    "id": "integer",
    "transaction_no": "string"
  },
  "deliveries": "array",
  "payment_transactions": "array",
  "invoices": "array",
  "person": {
    "id": "integer",
    "display_name": "string",
    "title": "string",
    "first_name": "string",
    "middle_name": "string",
    "last_name": "string",
    "tax_no": "string",
    "email": "string",
    "address": "string",
    "billing_address": "string",
    "phone": "string",
    "fax": "string",
    "mobile": "string",
    "tax_no": "string"
  },
  "discount_type": {
    "id": "integer",
    "name": "string",
    "name_bahasa": "string"
  },
  "warehouse": {
    "id": "integer",
    "name": "string",
    "code": "string",
    "status": "string"
  },
  "deposit_to": {
    "id": "integer",
    "name": "string",
    "number": "integer",
    "category": {
      "id": "integer",
      "name": "string"
    }
  },
  "term": {
    "id": "integer",
    "name": "string",
    "longetivity": "integer"
  },
  "tags": [
    {
      "id": "integer",
      "name": "string"
    },
    {
      "id": "integer",
      "name": "string"
    }
  ],
  "tags_string":"string",
  "has_payments": "boolean",
  "earliest_payment_date": {"type": "string","format": "date-time"},
  "tax": {
    "id": "integer",
    "name": "string",
    "rate": "string"
  },
  "tax_details": [
    {
      "name": "string",
      "tax_amount": "double",
      "tax_amount_currency_format": "string"
    }
  ],
  "use_tax_inclusive": "boolean",
  "attachments": "array",
  "email_previews": {
    "times_sent": "integer",
    "sent_to_list": "array"
  },
  "is_reconciled": "boolean",
  "updated_at": {"type": "string","format": "date-time"},
  "currency_code": "IDR",
  "currency_list_id": "integer",
  "currency_from_id": "integer",
  "currency_to_id": "integer",
  "multi_currency_id": "integer",
  "currency_rate": "integer",
  "company_currency": {
    "code": "string",
    "symbol": "string"
  }
}
```

## Example Response

```
{
    "kind": "Sales Order",
    "id": 4455088,
    "transaction_no": "10111",
    "token": "XY8xDfKNrximmSNQtOmh5Q",
    "email": "morgan@gmail.com, fadzil@gmail.com",
    "source": "v3/revamp",
    "address": "Jl. jalan ke sumedank",
    "message": "Test Default msg",
    "memo": "",
    "shipping_address": null,
    "is_shipped": false,
    "selected_po_id": null,
    "ship_via": "",
    "reference_no": "",
    "tracking_no": "",
    "status": "approved",
    "custom_id": null,
    "created_at": "2024-01-30T11:10:45.000Z",
    "deleted_at": null,
    "transaction_date": "30/01/2024",
    "due_date": "30/03/2024",
    "shipping_date": null,
    "original_amount": "10000.0",
    "remaining": "10000.0",
    "discount_unit": "0.0",
    "discount_price": "0.0",
    "shipping_price": "0.0",
    "amount_receive": "0.0",
    "tax_after_discount": true,
    "tax_amount": "0.0",
    "subtotal": "10000.0",
    "deposit": "0.0",
    "payment_received_amount": "0.0",
    "payment_received_amount_currency_format": "Rp.  0,00",
    "remaining_currency_format": "Rp.  10.000,00",
    "original_amount_currency_format": "Rp.  10.000,00",
    "shipping_price_currency_format": "Rp.  0,00",
    "tax_amount_currency_format": "Rp.  0,00",
    "discount_price_currency_format": "Rp.  0,00",
    "amount_receive_currency_format": "Rp.  0,00",
    "subtotal_currency_format": "Rp.  10.000,00",
    "deposit_currency_format": "Rp.  0,00",
    "discount_per_lines": "0.0",
    "discount_per_lines_currency_format": "Rp.  0,00",
    "tax": {
      "id": null,
      "name": null,
      "rate": null
    },
    "tax_details": [],
    "use_tax_inclusive": false,
    "deposit_to": {
      "id": null,
      "name": null,
      "number": null,
      "category": {
        "id": null,
        "name": null
      }
    },
    "transaction_status": {
      "id": 1,
      "name": "Open",
      "name_bahasa": "Belum Dibayar"
    },
    "transaction_lines_attributes": [
      {
        "id": 4670179,
        "custom_id": null,
        "description": "",
        "amount": "10000.0",
        "discount": "0.0",
        "rate": "10000.0",
        "tax": null,
        "line_tax": {
          "id": null,
          "name": null,
          "rate": null,
          "children": []
        },
        "amount_currency_format": "Rp.  10.000,00",
        "rate_currency_format": "Rp.  10.000,00",
        "has_return_line": false,
        "quantity": 1,
        "sell_acc_id": 30918337,
        "buy_acc_id": 30918340,
        "product": {
          "id": 14523140,
          "name": "A1 Morgan Ganteng",
          "code": null,
          "product_custom_id": null,
          "archive": false,
          "quantity": 0,
          "quantity_string": "0.0",
          "track_inventory": false,
          "sell_price_per_unit": "10000.0",
          "buy_price_per_unit": "0.0",
          "link": null
        },
        "unit": {
          "id": 83000,
          "name": "Buah"
        },
        "units": [],
        "pricing_rule": null,
        "remaining_quantity": 1
      }
    ],
    "person": {
      "id": 717245,
      "title": null,
      "first_name": "",
      "middle_name": "",
      "last_name": "",
      "display_name": "alicloudSRS",
      "email": "morgan@gmail.com, fadzil@gmail.com",
      "address": "Jl. jalan ke Dufan",
      "billing_address": "Jl. jalan ke sumedank",
      "phone": "0895355293048",
      "fax": "",
      "mobile": "",
      "tax_no": ""
    },
    "discount_type": {
      "id": 1,
      "name": "Percent",
      "name_bahasa": "Persen"
    },
    "warehouse": {
      "id": null,
      "name": null,
      "code": null,
      "status": null
    },
    "sales_quote": {
      "id": null,
      "transaction_no": null
    },
    "tags": null,
    "tags_string": "",
    "term": {
      "id": 296675,
      "name": "Net 60",
      "longetivity": 60
    },
    "is_reconciled": false,
    "attachments": [],
    "payments": [],
    "deliveries": [],
    "payment_transactions": [],
    "invoices": [],
    "updated_at": "2024-01-30T11:10:45.000Z",
    "currency_code": "IDR",
    "currency_list_id": 8438,
    "currency_from_id": 1,
    "currency_to_id": 1,
    "multi_currency_id": 133371,
    "currency_rate": 1,
    "company_currency": {
      "code": "IDR",
      "symbol": "Rp."
    }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/jurnal/send-sales-quote
title: Send Sales Quote - Mekari Developers Documentation
---

# Send Sales Quote to Webhook Consumer Every New Sales Quote Created

## Prequisite to Consume

1. Feature sales quote webhook for that company is active in [Jurnal](https://jurnal.id)- User need to create new sales quote

## Event

```
jurnal.salesquote.created
```

## Schema

```
{
        "kind": "string",
        "id": "integer",
        "transaction_no": "string",
        "email": "string",
        "address": "string",
        "message": "string",
        "memo": "string",
        "remaining": "string",
        "original_amount": "string",
        "discount_price": "string",
        "shipping_price": "string",
        "shipping_address": "string",
        "is_shipped": "boolean",
        "ship_via": "string",
        "subtotal": "string",
        "reference_no": "string",
        "tracking_no": "string",
        "tax_after_discount": "boolean",
        "discount_unit": "string",
        "tax_amount": "string",
        "status": "string",
        "custom_id": "string",
        "created_at": {"type": "string","format": "date-time"},
        "deleted_at": {"type": "string","format": "date-time"},
        "deletable": "boolean",
        "editable": "boolean",
        "audited_by": "string",
        "transaction_date": {"type": "string","format": "date"},
        "expiry_date": {"type": "string","format": "date"},
        "shipping_date": {"type": "string","format": "date"},
        "remaining_currency_format": "string",
        "shipping_price_currency_format": "string",
        "tax_amount_currency_format": "string",
        "discount_price_currency_format": "string",
        "subtotal_currency_format": "string",
        "discount_per_lines": "string",
        "discount_per_lines_currency_format": "string",
        "transaction_status": {
            "id": "integer",
            "name": "string",
            "name_bahasa": "string"
        },
        "transaction_lines_attributes": [
            {
                "id": "integer",
                "custom_id": "string",
                "description": "string",
                "amount": "string",
                "discount": "string",
                "rate": "string",
                "tax": "string",
                "line_tax": {
                    "id": "integer",
                    "name": "string",
                    "rate": "string",
                    "children": "array"
                },
                "amount_currency_format": "string",
                "rate_currency_format": "string",
                "has_return_line": "boolean",
                "quantity": "double",
                "sell_acc_id": "integer",
                "buy_acc_id": "integer",
                "product": {
                    "id": "integer",
                    "name": "string",
                    "code": "string",
                    "product_custom_id": "string",
                    "archive": "boolean",
                    "quantity": "double",
                    "quantity_string": "string",
                    "track_inventory": "boolean",
                    "sell_price_per_unit": "string",
                    "buy_price_per_unit": "string",
                    "link": "string"
                },
                "unit": {
                    "id": "integer",
                    "name": "string"
                },
                "units": "array",
                "pricing_rule": "array"
            }
        ],
        "person": {
            "id": "integer",
            "display_name": "Adam",
            "email": "string",
            "address": "string",
            "phone": "string",
            "fax": "string"
        },
        "discount_type": {
            "id": "integer",
            "name": "string",
            "name_bahasa": "string"
        },
        "term": {
            "id": "integer",
            "name": "string",
            "longetivity": "integer"
        },
        "tax": {
            "id": "integer",
            "name": "string",
            "rate": "string"
        },
        "tax_details": [
            {
                "name": "string",
                "tax_amount": "double",
                "tax_amount_currency_format": "string"
            }
        ],
        "use_tax_inclusive": "boolean",
        "tags": [
            {
                "id": "integer",
                "name": "string"
            },
            {
                "id": "integer",
                "name": "string"
            }
        ],
        "tags_string": "string",
        "updated_at": {"type": "string","format": "date-time"},
        "currency_code": "string",
        "disable_link": "boolean"
}
```

## Example Response

```
{
        "kind": "Sales Quote",
        "id": 15192,
        "transaction_no": "10004",
        "email": "email@budi.com",
        "address": "Jalan Pengiriman X, Jakarta",
        "message": "message note",
        "memo": "memo note",
        "remaining": "3291624.0",
        "original_amount": "3291624.0",
        "discount_price": "64800.0",
        "shipping_price": "0.0",
        "shipping_address": null,
        "is_shipped": false,
        "ship_via": null,
        "subtotal": "3600000.0",
        "reference_no": "customer_100",
        "tracking_no": null,
        "tax_after_discount": true,
        "discount_unit": "2.0",
        "tax_amount": "116424.0",
        "status": "approved",
        "custom_id": null,
        "created_at": "2023-11-07T08:09:45.647Z",
        "deleted_at": null,
        "deletable": true,
        "editable": true,
        "audited_by": null,
        "transaction_date": "07/11/2023",
        "expiry_date": "07/12/2023",
        "shipping_date": null,
        "remaining_currency_format": "Rp.  3.291.624,00",
        "shipping_price_currency_format": "Rp.  0,00",
        "tax_amount_currency_format": "Rp.  116.424,00",
        "discount_price_currency_format": "Rp.  64.800,00",
        "subtotal_currency_format": "Rp.  3.600.000,00",
        "discount_per_lines": "360000.0",
        "discount_per_lines_currency_format": "Rp.  360.000,00",
        "transaction_status": {
            "id": 1,
            "name": "Open",
            "name_bahasa": "Belum Dibayar"
        },
        "transaction_lines_attributes": [
            {
                "id": 15181,
                "custom_id": null,
                "description": "Desc Mac",
                "amount": "1080000.0",
                "discount": "10.0",
                "rate": "1200000.0",
                "tax": null,
                "line_tax": {
                    "id": 1,
                    "name": "PPN",
                    "rate": "11.0",
                    "children": []
                },
                "amount_currency_format": "Rp.  1.080.000,00",
                "rate_currency_format": "Rp.  1.200.000,00",
                "has_return_line": false,
                "quantity": 1.0,
                "sell_acc_id": 148,
                "buy_acc_id": 150,
                "product": {
                    "id": 2,
                    "name": "Macbook 1",
                    "code": "",
                    "product_custom_id": null,
                    "archive": false,
                    "quantity": 0.0,
                    "quantity_string": "0.0",
                    "track_inventory": false,
                    "sell_price_per_unit": "1200000.0",
                    "buy_price_per_unit": "1000000.0",
                    "link": "http://localhost:3000/products/2"
                },
                "unit": {
                    "id": 1,
                    "name": "Pcs"
                },
                "units": [],
                "pricing_rule": null
            }
        ],
        "person": {
            "id": 5,
            "display_name": "Adam",
            "email": "",
            "address": null,
            "phone": null,
            "fax": null
        },
        "discount_type": {
            "id": 1,
            "name": "Percent",
            "name_bahasa": "Persen"
        },
        "term": {
            "id": 1,
            "name": "Net 30",
            "longetivity": 30
        },
        "tax": {
            "id": null,
            "name": null,
            "rate": null
        },
        "tax_details": [
            {
                "name": "PPN 11.0%",
                "tax_amount": 116424.0,
                "tax_amount_currency_format": "Rp.  116.424,00"
            }
        ],
        "use_tax_inclusive": false,
        "tags": [
            {
                "id": 6,
                "name": "tags one"
            },
            {
                "id": 7,
                "name": "tags two"
            }
        ],
        "tags_string": "tags one, tags two",
        "updated_at": "2023-11-07T08:09:45.647Z",
        "currency_code": "IDR",
        "disable_link": false
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta
title: Talenta - Mekari Developers Documentation
---

# Talenta

---

## Table of contents

* [Notify users when add new employee](/docs/kb/webhooks/talenta/talenta-employee-detail-created)* [Notify users when updated data employee](/docs/kb/webhooks/talenta/talenta-employee-detail-updated)* [Notify users when deleted employee](/docs/kb/webhooks/talenta/talenta-employee-detail-deleted)* [Notify users when approved transfer employee](/docs/kb/webhooks/talenta/talenta-employee-transfer-approved)* [Notify users when cancel transfer employee employee](/docs/kb/webhooks/talenta/talenta-employee-transfer-cancelled)* [Notify users when created resignation](/docs/kb/webhooks/talenta/talenta-employee-resignation-created)* [Notify users when cancelled resignation](/docs/kb/webhooks/talenta/talenta-employee-resignation-cancelled)* [Create Loan based on form submission](/docs/kb/webhooks/talenta/talenta-forms-entry-approved)* [Live Attendance](/docs/kb/webhooks/talenta/talenta-attendance-liveattendance)* [Live Attendance Bluebird](/docs/kb/webhooks/talenta/talenta-attendance-liveattendance-bluebird)* [Payroll Payslip Wabaqontak](/docs/kb/webhooks/talenta/talenta-payroll-payslip-wabaqontak)* [Attendance Scheduler Change Schedule](/docs/kb/webhooks/talenta/talenta-attendance-scheduler-changeschedule)* [Attendance Scheduler Change Shift](/docs/kb/webhooks/talenta/talenta-attendance-scheduler-changeshift)

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-employee-detail-created
title: Notify users when add new employee - Mekari Developers Documentation
---

# Notify users when add new employee

## Prequisite to consume

The event will be triggered when

1. There is a new employee via bulk update- There is a new employee via add new employee- There is a new employee added after approval process

## Event

```
talenta.employee.detail.created
```

## Schema

```
{
  "personal": {
    "first_name": String,
    "last_name": String,
    "barcode": String,
    "email": String,
    "identity_type": String,
    "identity_number": String,
    "expired_date_identity_id": String,
    "postal_code": String,
    "address": String,
    "current_address": String,
    "birth_place": String,
    "birth_date": Date,
    "phone": String,
    "mobile_phone": String,
    "gender": String,
    "marital_status": String,
    "blood_type": String,
    "religion": String,
    "avatar": String
  },
  "family": {
    "members": [
      {
        "id": Number,
        "full_name": String,
        "relationship": String,
        "relationship_id": Number,
        "birth_date": Date,
        "no_ktp": String,
        "marital_status": String,
        "gender": String,
        "job": String,
        "religion": String,
        "is_deleted": Number,
        "created_at": Date,
        "updated_at": Date
      },
      {
        "id": Number,
        "full_name": String,
        "relationship": String,
        "relationship_id": Number,
        "birth_date": Date,
        "no_ktp": String,
        "marital_status": String,
        "gender": String,
        "job": String,
        "religion": String,
        "is_deleted": Number,
        "created_at": String,
        "updated_at": String
      },
      {
        "id": Number,
        "full_name": String,
        "relationship": String,
        "relationship_id": Number,
        "birth_date": Date,
        "no_ktp": String,
        "marital_status": String,
        "gender": String,
        "job": String,
        "religion": String,
        "is_deleted": Number,
        "created_at": String,
        "updated_at": String
      }
    ],
    "emergency_contacts": [
      {
        "full_name": String,
        "relationship": String,
        "birth_date": String,
        "no_ktp": String,
        "marital_status": String,
        "gender": String,
        "job": String,
        "religion": String
      },
      {
        "full_name": String,
        "relationship": String,
        "birth_date": String,
        "no_ktp": String,
        "marital_status": String,
        "gender": String,
        "job": String,
        "religion": String
      }
    ]
  },
  "education": {
    "formal_education_history": [
    {
      "education_degree": String,
      "institution_name":  String,
      "majors": String,
      "year_from": String,
      "year_to": String,
      "score": String
    }
    ],
    "informal_education_history": [{
      "id": Number,
      "user_id": Number,
      "company_id": Number,
      "held_by_institution_name": String,
      "name": String,
      "duration": Number,
      "duration_type": Number,
      "fee": String,
      "certification": Boolean,
      "start_date": Date,
      "end_date": Date,
      "reference_id": Number,
      "filename": String,
      "description": String,
      "create_date": Date,
      "update_date": Date
      }
    ]
  },
  "employment": {
    "employee_id": String,
    "company_id": Number,
    "organization_id": Number,
    "organization_name": String,
    "job_position_id": Number,
    "job_position": String,
    "job_level_id": Number,
    "job_level": String,
    "employement_status_id": Number,
    "employment_status": String,
    "branch_id": Number,
    "branch": String,
    "join_date": Date,
    "length_of_service": String,
    "grade": String,
    "class":String,
    "approval_line": Number,
    "approval_line_employee_id": String,
    "status": String,
    "resign_date": String,
    "working_experiences": [],
    "sign_date": Date,
    "sbu": [
      {
        "field_id": Number,
        "field_name": String,
        "value_id": null,
        "value_name": null,
        "value_code": null
      }
    ]
  },
  "payroll_info": {
    "bpjs_ketenagakerjaan": String,
    "bpjs_kesehatan": String,
    "npwp": String,
    "bank_id": Number,
    "bank_name": String,
    "bank_account": String,
    "bank_account_holder": String,
    "ptkp_status": "TK/0",
    "bank_code": String,
    "cost_center_id": Number,
    "cost_center_name": String,
    "cost_center_category_id": Number,
    "cost_center_category_name": String,
    "employee_tax_status": Number,
    "nationality_code": String,
    "expatriatedn_date": String,
    "created_at": Date,
    "updated_at": Date
  },
  "custom_field": [
    {
      "field_name": Date,
      "value": String
    }
  ],
  "access_role": {
    "id": Number,
    "name": String,
    "role_id": Number,
    "role_name": String,
    "role_type": String
  }
}
```

## Example Response

```
{
  "personal": {
    "first_name": "SDET",
    "last_name": "Superadmin",
    "barcode": "MKR861",
    "email": "sdet-automation+test61@mekari.com",
    "identity_type": "KTP",
    "identity_number": "",
    "expired_date_identity_id": "",
    "postal_code": "",
    "address": "",
    "current_address": "",
    "birth_place": "Johor Baru",
    "birth_date": "1992-07-08",
    "phone": "",
    "mobile_phone": "",
    "gender": "Male",
    "marital_status": "Married",
    "blood_type": "AB",
    "religion": "Islam",
    "avatar": "https://development-test2.s3.ap-southeast-1.amazonaws.com/avatar/24INn05dp_aR9P2_LdZrPmLWKLPUDYbL.png?X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=FwoGZXIvYXdzECIaDCN2L8MBwg%2B0LRKuIiLDAXiMYm5A4AEHNaunWBbuIn6ZUBzmOVQvvj1VBlYNYxQHAGQEL%2F4RNQcTyzQCs8%2B%2BCXzRwpdBPGOtX%2BXRQ05cFxJkdeW3VXEBhTzb3tAN3Zl1qwLySB9rxFO8JbU9GvcSSezSGuf1ieqQlzfexueuH%2Fss02Juxj2ZoX4YOTYmrZty3XEBIDtLALvWmzTD6%2BAjfKWRziOWYfG9PQ2BMvgO4qXPkw2wTXqCdaVdR5m4nErSzT%2BnVegxXnbyH53xuf2xays%2BTCi3z6OMBjIt0wIwyHTK7NNFbTg5iAKLx9IQNjaqu0KRqdIE7UVLFKjQLYe%2Bv4uBOVW3cP7f&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA3A7QLOC3I44ZUHDE%2F20211108%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Date=20211108T090648Z&X-Amz-SignedHeaders=host&X-Amz-Expires=1800&X-Amz-Signature=4327cc2f9e851f12724ed4076fdd05d3950ab4b730e9bfd671a714ceff21ec7c"
  },
  "family": {
    "members": [
      {
        "id": 17536,
        "full_name": "ahmad leo",
        "relationship": "Mother",
        "relationship_id": 11,
        "birth_date": "2021-09-06",
        "no_ktp": "",
        "marital_status": "",
        "gender": "Male",
        "job": "",
        "religion": "",
        "is_deleted": 0,
        "created_at": "2021-09-06 15:11:14",
        "updated_at": "2021-09-06 15:11:14"
      },
      {
        "id": 17545,
        "full_name": "Sekala Niskala",
        "relationship": "Sibling",
        "relationship_id": 2,
        "birth_date": "1990-12-05",
        "no_ktp": "310202010101010",
        "marital_status": "Married",
        "gender": "Male",
        "job": "Detektif Swasta",
        "religion": "Catholic",
        "is_deleted": 0,
        "created_at": "2021-09-22 12:34:35",
        "updated_at": "2021-09-22 12:34:35"
      },
      {
        "id": 17546,
        "full_name": "Akan didelete",
        "relationship": "Cousin",
        "relationship_id": 20,
        "birth_date": "1944-02-16",
        "no_ktp": "",
        "marital_status": "",
        "gender": "Female",
        "job": "",
        "religion": "",
        "is_deleted": 1,
        "created_at": "2021-09-22 12:37:29",
        "updated_at": "2021-09-22 12:43:38"
      }
    ],
    "emergency_contacts": [
      {
        "full_name": "eren yeager",
        "relationship": "Father",
        "birth_date": "",
        "no_ktp": "",
        "marital_status": "",
        "gender": "",
        "job": "",
        "religion": ""
      },
      {
        "full_name": "Sekala Niskala",
        "relationship": "Sibling",
        "birth_date": "",
        "no_ktp": "",
        "marital_status": "",
        "gender": "",
        "job": "",
        "religion": ""
      }
    ]
  },
  "education": {
    "formal_education_history": [
    {
      "education_degree": "String",
      "institution_name": "String",
      "majors":"String",
      "year_from":"String",
      "year_to":"String",
      "score":"String"
    }
    ],
    "informal_education_history": [{
      "id": 3254,
      "user_id": 935848,
      "company_id": 3053,
      "held_by_institution_name": "Lembaga Iusto.",
      "name": "Course Et.",
      "duration": 31,
      "duration_type": 1,
      "fee": "118329",
      "certification": true,
      "start_date": "2021-12-27",
      "end_date": "2022-01-26",
      "reference_id": 28,
      "filename": "https://development-test2.s3.ap-southeast-1.amazonaws.com/myinfo/training/wLQJlpLmUnsNs_eBKI8nsxdZYOAC2zyx.png?X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=FwoGZXIvYXdzEGIaDEHJfsTsVA9hzVtPoiLDATIPTwZqJeLdMPBLd62hpNghK7HvUCETforSrmSQrYeGlj6mPcFVIhj2Rb7lS0D79BMdFjcSghrrR%2BKRlrVV1knhlcXtaRlF5gLulIfX7Qk00f5mjrWeIxJ1HEIcSA2AkXgzDE57yr50nwtDSyfUIQYgBcD%2FZ%2B%2BIPxq03ig6jRa29Z6rM23bVxLliH%2BZ3U6GOEUsPTQ7Rhnr1QhPJ3YvUm7pizf9nSI0uvCbe0dbwvZAA7Rw9bmHTBxPceWVJ6v%2BonQjwyi3yvOPBjItznPnejlaj2WDqSop0O5HpBVdp2V5Tc5QTlxPz4daK9NZGkMaid2uXiINv5AW&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIA3A7QLOC3AF6TD7NE%2F20220204%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Date=20220204T083720Z&X-Amz-SignedHeaders=host&X-Amz-Expires=1800&X-Amz-Signature=7f422cd28f47ac5ccdec439f74bb1b91f07945eaa43da46a75be18c5909e6dfb",
      "description": "",
      "create_date": "2022-01-27 10:40:09",
      "update_date": "2022-01-27 10:40:09"
      }
    ]
  },
  "employment": {
    "employee_id": "SDET-001",
    "company_id": 3053,
    "organization_id": 20392,
    "organization_name": "IT Division",
    "job_position_id": 20392,
    "job_position": "Staff IT",
    "job_level_id": 20392,
    "job_level": "Manager",
    "employement_status_id": 20392,
    "employment_status": "employment status dont delete",
    "branch_id": 0,
    "branch": "Pusat",
    "join_date": "2018-01-08",
    "length_of_service": "3 Year 10 Month 1 Day",
    "grade": "Grade 1",
    "class": "Class A",
    "approval_line": 935853,
    "approval_line_employee_id": "SDET-002",
    "status": "Active",
    "resign_date": "",
    "working_experiences": [],
    "sign_date": "2024-04-16",
    "sbu": [
      {
        "field_id": 4,
        "field_name": "group 1",
        "value_id": null,
        "value_name": null,
        "value_code": null
      }
    ]
  },
  "payroll_info": {
    "bpjs_ketenagakerjaan": "",
    "bpjs_kesehatan": "",
    "npwp": "",
    "bank_id": 0,
    "bank_name": "-",
    "bank_account": "",
    "bank_account_holder": "",
    "ptkp_status": "TK/0",
    "bank_code": "",
    "cost_center_id": 71,
    "cost_center_name": "COST CENTER DONT DELETE",
    "cost_center_category_id": 1,
    "cost_center_category_name": "Direct",
    "employee_tax_status": 0,
    "nationality_code": "",
    "expatriatedn_date": "",
    "created_at": "2020-11-13 14:11:56",
    "updated_at": "2021-10-19 17:30:22"
  },
  "custom_field": [
    {
      "field_name": "level",
      "value": ""
    }
  ],
  "access_role": {
    "id": 1,
    "name": "Super Admin",
    "role_id": 1,
    "role_name": "Super Admin",
    "role_type": "default"
  }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-employee-detail-updated
title: Notify users when updated data employee - Mekari Developers Documentation
---

# Notify users when updated data employee

## Prequisite to consume

The event will be triggered when

1. There is a data that edited by client via single edit- There is a data that edited by client vi bulk edit- Employee transfer is executed or cancelled that impact to the employee detail- Resignation created

## Event

```
talenta.employee.detail.updated
```

## Schema

```
{
  "user_id": Number,
  "personal": {
    "first_name": String,
    "last_name": String,
    "barcode": String,
    "email": String,
    "identity_type": String
  },
  "family": {
    "members": [
      {
        "id": Number,
        "full_name": String,
        "relationship": String,
        "relationship_id": Number
      }
    ],
    "emergency_contacts": [
      {
        "full_name": String,
        "relationship": String
      }
    ]
  },
  "education": {
      "formal_education_history": [
        {
          "education_degree": String,
          "institution_name": String,
          "majors": String,
          "year_from": String,
          "year_to": String,
          "score": String
        }
      ],
      "informal_education_history": [
        {
          "id": Number,
          "user_id": Number,
          "company_id": Number
        }
      ]
  },
  "employment": {
    "employee_id": String,
    "company_id": Number,
    "organization_id": Number,
    "organization_name": String
    "sign_date": Date,
    "sbu": [
      {
        "field_id": Number,
        "field_name": String,
        "value_id": null,
        "value_name": null,
        "value_code": null
      }
    ]
  },
  "payroll_info": {
    "bpjs_ketenagakerjaan": String,
    "bpjs_kesehatan": String,
    "npwp": String
  },
  "custom_field": [
    {
      "field_name": String,
      "value": String
    }
  ],
  "access_role": {
    "id": Number,
    "name": String
  }
}
```

## Example Response

```
{
  "user_id": 12321412,
  "personal": {
    "first_name": "SDET",
    "last_name": "Superadmin",
    "barcode": "MKR861",
    "email": "sdet-automation+test61@mekari.com",
    "identity_type": "KTP"
  },
  "family": {
    "members": [
      {
        "id": 17536,
        "full_name": "ahmad leo",
        "relationship": "Mother",
        "relationship_id": 11
      }
    ],
    "emergency_contacts": [
      {
        "full_name": "eren yeager",
        "relationship": "Father"
      }
    ]
  },
  "education": {
    "formal_education_history": [
      {
        "education_degree": "String",
        "institution_name": "String",
        "majors": "String",
        "year_from": "String",
        "year_to": "String",
        "score": "String"
      }
    ],
    "informal_education_history": [
      {
        "id": 3254,
        "user_id": 935848,
        "company_id": 3053
      }
    ]
  },
  "employment": {
    "employee_id": "SDET-001",
    "company_id": 3053,
    "organization_id": 20392,
    "organization_name": "IT Division",
    "sign_date": "2024-04-16",
    "sbu": [
      {
        "field_id": 4,
        "field_name": "group 1",
        "value_id": null,
        "value_name": null,
        "value_code": null
      }
    ]
  },
  "payroll_info": {
    "bpjs_ketenagakerjaan": "",
    "bpjs_kesehatan": "",
    "npwp": ""
  },
  "custom_field": [
    {
      "field_name": "level",
      "value": ""
    }
  ],
  "access_role": {
    "id": 1,
    "name": "Super Admin"
  }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-employee-detail-deleted
title: Notify users when deleted employee - Mekari Developers Documentation
---

# Notify users when deleted employee

## Prequisite to consume

1. If there is a deleted employee data.

## Event

```
talenta.employee.detail.deleted
```

## Schema

```
{
  "user_id": Number,
  "personal": Object,
  "family": Object,
  "education": Object,
  "employment": Object,
  "payroll_info": Object,
  "custom_field": Array,
  "access_role": Object
}
```

## Example Response

```
{
  "user_id": 12321412,
  "first_name": "SDET",
  "last_name": "Superadmin",
  "email": "sdet-automation+test61@mekari.com",
  "employee_id": "SDET-001",
  "company_id": 3053,
  "organization_id": 20392,
  "organization_name": "IT Division"
}
```

# 4. Notify users when approved transfer employee

## Prequisite to consume

1. If there is a employee transfer approved

## Event

```
talenta.employee.transfer.approved
```

## Schema

```
{
  "user_id": Number,
  "old_employment": {
    "effective date": String,
    "employee_id": String,
    "company_id": Number,
    "organization_id": Number,
    "organization_name": String,
    "job_position_id": Number,
    "job_position": String,
    "job_level_id": Number,
    "job_level": String,
    "employement_status_id": Number,
    "employment_status": String,
    "branch_id": Number,
    "branch": String,
    "grade": String,
    "class": String,
    "approval_line": Number,
    "approval_line_employee_id": String,
    "status": String,
    "effective_date": String,
  },
  "new_employment": {
    "effective date": String,
    "employee_id": String,
    "company_id": Number,
    "organization_id": Number,
    "organization_name": String,
    "job_position_id": Number,
    "job_position": String,
    "job_level_id": Number,
    "job_level": String,
    "employement_status_id": Number,
    "employment_status": String,
    "branch_id": Number,
    "branch": String,
    "grade": String,
    "class": String,
    "approval_line": Number,
    "approval_line_employee_id": String,
    "status": String,
    "effective_date": String,
  }
}
```

## Example Response

```
{
  "user_id": "integer",
  "old_employment": {
    "effective date": "string",
    "employee_id": "string",
    "company_id": "integer",
    "organization_id": "integer",
    "organization_name": "string",
    "job_position_id": "integer",
    "job_position": "string",
    "job_level_id": "integer",
    "job_level": "string",
    "employement_status_id": "integer",
    "employment_status": "string",
    "branch_id": "integer",
    "branch": "string",
    "grade": "string",
    "class": "string",
    "approval_line": "integer",
    "approval_line_employee_id": "string",
    "status": "string",
    "effective_date": "string",
  },
  "new_employment": {
    "effective date": "string",
    "employee_id": "string",
    "company_id": "integer",
    "organization_id": "integer",
    "organization_name": "string",
    "job_position_id": "integer",
    "job_position": "string",
    "job_level_id": "integer",
    "job_level": "string",
    "employement_status_id": "integer",
    "employment_status": "string",
    "branch_id": "integer",
    "branch": "string",
    "grade": "string",
    "class": "string",
    "approval_line": "integer",
    "approval_line_employee_id": "string",
    "status": "string",
    "effective_date": "string",
  }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-employee-transfer-approved
title: Notify users when approved transfer employee - Mekari Developers Documentation
---

# Notify users when approved transfer employee

## Prequisite to consume

1. If there is a employee transfer approved

## Event

```
talenta.employee.transfer.approved
```

## Schema

```
{
    "user_id": Number,
    "old_employment": {
        "effective date": String,
        "employee_id": String,
        "company_id": Number,
        "organization_id": Number,
        "organization_name": String,
        "job_position_id": Number,
        "job_position": String,
        "job_level_id": Number,
        "job_level": String,
        "employement_status_id": Number,
        "employment_status": String,
        "branch_id": Number,
        "branch": String,
        "grade": String,
        "class": String,
        "approval_line": Number,
        "approval_line_employee_id": String,
        "status": String,
        "effective_date": String,
    },
    "new_employment": {
        "effective date": String,
        "employee_id": String,
        "company_id": Number,
        "organization_id": Number,
        "organization_name": String,
        "job_position_id": Number,
        "job_position": String,
        "job_level_id": Number,
        "job_level": String,
        "employement_status_id": Number,
        "employment_status": String,
        "branch_id": Number,
        "branch": String,
        "grade": String,
        "class": String,
        "approval_line": Number,
        "approval_line_employee_id": String,
        "status": String,
        "effective_date": String,
    }
}
```

## Example Response

```
{
    "user_id": "integer",
    "old_employment": {
        "effective date": "string",
        "employee_id": "string",
        "company_id": "integer",
        "organization_id": "integer",
        "organization_name": "string",
        "job_position_id": "integer",
        "job_position": "string",
        "job_level_id": "integer",
        "job_level": "string",
        "employement_status_id": "integer",
        "employment_status": "string",
        "branch_id": "integer",
        "branch": "string",
        "grade": "string",
        "class": "string",
        "approval_line": "integer",
        "approval_line_employee_id": "string",
        "status": "string",
        "effective_date": "string",
    },
    "new_employment": {
        "effective date": "string",
        "employee_id": "string",
        "company_id": "integer",
        "organization_id": "integer",
        "organization_name": "string",
        "job_position_id": "integer",
        "job_position": "string",
        "job_level_id": "integer",
        "job_level": "string",
        "employement_status_id": "integer",
        "employment_status": "string",
        "branch_id": "integer",
        "branch": "string",
        "grade": "string",
        "class": "string",
        "approval_line": "integer",
        "approval_line_employee_id": "string",
        "status": "string",
        "effective_date": "string",
    }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-employee-transfer-cancelled
title: Notify users when cancel transfer employee employee - Mekari Developers Documentation
---

# Notify users when cancel transfer employee employee

## Prequisite to consume

1. If there is a employee transfer cancelled

## Event

```
talenta.employee.transfer.cancelled
```

## Schema

```
{
    "user_id": Number,
    "employment": {
        "employee_id": String,
        "company_id": Number,
        "organization_id": Number,
        "organization_name": String,
        "job_position_id": Number,
        "job_position": String,
        "job_level_id": Number,
        "job_level": String,
        "employement_status_id": Number,
        "employment_status": String,
        "branch_id": Number,
        "branch": String,
        "join_date": String,
        "length_of_service": String,
        "grade": String,
        "class": String,
        "approval_line": Number,
        "approval_line_employee_id": String,
        "status": String,
        "resign_date": String,
        "working_experiences": Array
    }
}
```

## Example Response

```
{
    "user_id": 12321412,
    "employment": {
        "employee_id": "SDET-001",
        "company_id": 3053,
        "organization_id": 20392,
        "organization_name": "IT Division",
        "job_position_id": 20392,
        "job_position": "Staff IT",
        "job_level_id": 20392,
        "job_level": "Manager",
        "employement_status_id": 20392,
        "employment_status": "employment status dont delete",
        "branch_id": 0,
        "branch": "Pusat",
        "join_date": "2018-01-08",
        "length_of_service": "3 Year 10 Month 1 Day",
        "grade": "Grade 1",
        "class": "Class A",
        "approval_line": 935853,
        "approval_line_employee_id": "SDET-002",
        "status": "Active",
        "resign_date": "",
        "working_experiences": []
    },
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-employee-resignation-created
title: Notify users when created resignation - Mekari Developers Documentation
---

# Notify users when created resignation

## Prequisite to consume

1. Triggered if there is employee resignation approved

## Event

```
talenta.employee.resignation.created
```

## Schema

```
{
    "user_id": Number,
    "employment": {
        "employee_id": String,
        "company_id": Number,
        "organization_id": Number,
        "organization_name": String,
        "job_position_id": Number,
        "job_position": String,
        "job_level_id": Number,
        "job_level": String,
        "employement_status_id": Number,
        "employment_status": String,
        "branch_id": Number,
        "branch": String,
        "join_date": String,
        "length_of_service": String,
        "grade": String,
        "class": String,
        "approval_line": Number,
        "approval_line_employee_id": String,
        "status": String,
        "resign_date": String,
        "working_experiences": Array
    }
}
```

## Example Response

```
{
    "user_id": 12321412,
    "employment": {
        "employee_id": "SDET-001",
        "company_id": 3053,
        "organization_id": 20392,
        "organization_name": "IT Division",
        "job_position_id": 20392,
        "job_position": "Staff IT",
        "job_level_id": 20392,
        "job_level": "Manager",
        "employement_status_id": 1,
        "employment_status": "Permanent",
        "branch_id": 0,
        "branch": "Pusat",
        "join_date": "2018-01-08",
        "length_of_service": "3 Year 10 Month 1 Day",
        "grade": "Grade 1",
        "class": "Class A",
        "approval_line": 935853,
        "approval_line_employee_id": "SDET-002",
        "status": "Active",
        "resign_date": "2023-02-25",
        "working_experiences": []
    }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-employee-resignation-cancelled
title: Notify users when cancelled resignation - Mekari Developers Documentation
---

# Notify users when cancelled resignation

## Prequisite to consume

1. Triggered if there is an employee resignation that cancelled

## Event

```
talenta.employee.resignation.cancelled
```

## Schema

```
{
    "user_id": Number,
    "employment": {
        "employee_id": String,
        "company_id": Number,
        "organization_id": Number,
        "organization_name": String,
        "job_position_id": Number,
        "job_position": String,
        "job_level_id": Number,
        "job_level": String,
        "employement_status_id": Number,
        "employment_status": String,
        "branch_id": Number,
        "branch": String,
        "join_date": String,
        "length_of_service": String,
        "grade": String,
        "class": String,
        "approval_line": Number,
        "approval_line_employee_id": String,
        "status": String,
        "resign_date": String,
        "working_experiences": Array
    }
}
```

## Example Response

```
{
    "user_id": 12321412,
    "employment": {
        "employee_id": "SDET-001",
        "company_id": 3053,
        "organization_id": 20392,
        "organization_name": "IT Division",
        "job_position_id": 20392,
        "job_position": "Staff IT",
        "job_level_id": 20392,
        "job_level": "Manager",
        "employement_status_id": 20392,
        "employment_status": "employment status dont delete",
        "branch_id": 0,
        "branch": "Pusat",
        "join_date": "2018-01-08",
        "length_of_service": "3 Year 10 Month 1 Day",
        "grade": "Grade 1",
        "class": "Class A",
        "approval_line": 935853,
        "approval_line_employee_id": "SDET-002",
        "status": "Active",
        "resign_date": "",
        "working_experiences": []
    },
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-forms-entry-approved
title: Create Loan based on form submission - Mekari Developers Documentation
---

# Create Loan based on form submission

## Prequisite to consume

The event will be triggered when

* certain form submission is approved by the approval

## Event

```
talenta.forms.entry.approved
```

## Schema

```
{
  "request": {
    "id": Number,
    "user_id": Number,
    "template_id": Number,
    "created_date": Timestamp,
    "updated_date": Timestamp,
    "status": Number,
    "last_approval_id": Number,
    "superadmin_sso_id": String,
    "request_detail": [
        {
          "id": Number,
          "question_id": Number,
          "type": Number,
          "value": String
        },
        {
          "id": Number,
          "question_id": Number,
          "type": Number,
          "value": String
        },
        {
          "id": Number,
          "question_id": Number,
          "type": Number,
          "value": String
        },
        {
          "id": Number,
          "question_id": Number,
          "type": Number,
          "value": String
        },
        ...
      ],
    "template": {
      "id": Number,
      "name": String,
      "creator": Number,
      "company_id": Number,
      "category": Number
    },
    "loan": {
      "loan_name_id": Number,
    }
  }
}
```

## Example Response

```
{
  "request": {
    "id":1,
    "user_id":9611,
    "template_id":1,
    "created_date":"2023-01-01 00:00:00",
    "updated_date":"2023-01-01 00:00:00",
    "status":1,
    "last_approval_id":8002,
    "superadmin_sso_id": String,
    "request_detail": [
        {
          "id":1,
          "question_id":1,
          "type":10,
          "value":"2023-01-01" // tanggal masuk
        },
        {
          "id":2,
          "question_id":2,
          "type":4,
          "value":"XL" // ukuran baju
        },
        {
          "id":3,
          "question_id":3,
          "type":4,
          "value":"Yes" // butuh topi
        },
        {
          "id":4,
          "question_id":4,
          "type":4,
          "value":"Yes" // butuh apron
        },
        {
          "id":5,
          "question_id":5,
          "type":11,
          "value":"Lorem Ipsum" // Keterangan
        },
      ],
    "template": {
      "id":1,
      "name":"Form Pengajuan Loan",
      "creator":8002,
      "company_id":679,
      "category":3
    },
    "loan": {
      "loan_name_id":123,
    }
  }
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-attendance-liveattendance
title: Live Attendance - Mekari Developers Documentation
---

# Live Attendance

## Event

```
talenta.attendance.liveattendance
```

## Schema

```
{
   "user_id": Number,
    "employee_id": String,
    "email": String,
    "company_id": Number,
    "date": String,
    "shift": String,
    "schedule_in": ,
    "schedule_out": time,
    "final_check_in": time,
    "final_check_out": time,
    "schedule_break_in": time,
    "schedule_break_out": time,
    "time": timestamp
    "location": String,
    "coordinate": String,
    "description": String,
    "source": String,
    "type": String,
    "locations": [
      {
        "id": Number,
        "setting_id": Number,
        "name": String,
        "radius": Number,
        "latitude": String,
        "longitude": String,
        "address": String,
      }
    ]
}
```

## Example Response

```
{
   "user_id": 333312,
    "employee_id": "MKR-1045",
    "email": "teo.wijayarto@mekari.com",
    "company_id": 3620,
    "date": "2021-03-02",
    "shift": "office",
    "schedule_in": "09:00:00",
    "schedule_out": "18:00:00",
    "final_check_in": "18:45:40",
    "final_check_out": "07:00:00",
    "schedule_break_in": "07:00:00",
    "schedule_break_out": "07:00:00",
    "time": "2021-03-02 18:50:01",
    "location": "-",
    "coordinate": "-6.1429812,106.7813307",
    "description": "test production API",
    "source": "Mobile Apps",
    "type": "CI",
    "locations": [
      {
        "id": 1291892,
        "setting_id": 8724,
        "name": "Home",
        "radius": 200,
        "latitude": "-6.209403",
        "longitude": "106.8208889",
        "address": "Chugoku Paints Indonesia PT, Jakarta Pusat 10220, Indonesia",
      }
    ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-attendance-liveattendance-bluebird
title: Live Attendance Bluebird - Mekari Developers Documentation
---

# Live Attendance Bluebird

## Event

```
talenta.attendance.liveattendance.bluebird
```

## Schema

```
{
   "user_id": Number,
    "organization_user_id": Number,
    "email": String,
    "company_id": Number,
    "clock_date": String,
    "shift": String,
    "schedule_in": ,
    "schedule_out": Time,
    "final_check_in": Time,
    "final_check_out": Time,
    "schedule_break_in": Time,
    "schedule_break_out": Time,
    "clock_time": Timestamp,
    "location_name": String,
    "coordinate": String,
    "description": String,
    "source": String,
    "event_type": Number,
    "locations": [
      {
        "id": Number,
        "setting_id": Number,
        "name": String,
        "radius": Number,
        "latitude": String,
        "longitude": String,
        "address": String,
      }
    ]
}
```

## Example Response

```
{
   "user_id": 333312,
    "employee_id": "MKR-1045",
    "email": "teo.wijayarto@mekari.com",
    "company_id": 3620,
    "date": "2021-03-02",
    "shift": "office",
    "schedule_in": "09:00:00",
    "schedule_out": "18:00:00",
    "final_check_in": "18:45:40",
    "final_check_out": "07:00:00",
    "schedule_break_in": "07:00:00",
    "schedule_break_out": "07:00:00",
    "time": "2021-03-02 18:50:01",
    "location": "-",
    "coordinate": "-6.1429812,106.7813307",
    "description": "test production API",
    "source": "Mobile Apps",
    "type": "CI",
    "locations": [
      {
        "id": 1291892,
        "setting_id": 8724,
        "name": "Home",
        "radius": 200,
        "latitude": "-6.209403",
        "longitude": "106.8208889",
        "address": "Chugoku Paints Indonesia PT, Jakarta Pusat 10220, Indonesia",
      }
    ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-payroll-payslip-wabaqontak
title: Payroll Payslip Wabaqontak - Mekari Developers Documentation
---

# Payroll Payslip Wabaqontak

## Event

```
talenta.payroll.payslip.wabaqontak
```

## Schema

```
{
   "user_id": int,
   "employee_id": string,
   "fullname": string,
   "phone_number": string,
   "month":string,
   "year": string,
   "message": string,
   "payslip_link":string,
   "publish_time":timestamp
}
```

## Example Response

```
{
   "user_id": 333312,
   "employee_id": "MKR-1045",
   "fullname": "Teo Wijayarto",
   "phone_number": "+628111223344",
   "month": "December",
   "year": "2023",
   "message": "Klik link dibawah untuk mengakses payslip anda.",
   "payslip_link": "https://hr.talenta.co/report/payslip?id=109140993&month=12&year=2023",
   "publish_time":"2023-03-22 12:00:11"
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-attendance-scheduler-changeschedule
title: Attendance Scheduler Change Schedule - Mekari Developers Documentation
---

# Attendance Scheduler Change Schedule

## Event

```
talenta.attendance.scheduler.changeschedule
```

## Schema

```
{
 "company_id": Number,
 "changes": [
   {
     "schedule_id": Number,
     "schedule_name": String,
     "effective date": String
     "employee_id": String,
     "employee_name":String,
     "user_id": Number,
     "shifts": [
       {
         "pattern_order": Number,
         "shift_name": String,
         "schedule_in": String,
         "schedule_out": String,
         "break_start": String,
         "break_end": String
       },
       {
         "pattern_order": Number,
         "shift_name": String,
         "schedule_in": String,
         "schedule_out": String,
         "break_start": String,
         "break_end": String
       }
     ]
   }
 ]
}
```

## Example Response

```
{
 "company_id": 1212,
 "changes": [
   {
     "schedule_id": 123213132,
     "schedule_name": "Jadwal kerja pool",
     "effective date": "23-12-2024",
     "employee_id": "emp001",
     "employee_name": "asep",
     "user_id": 1212,
     "shifts": [
       {
         "pattern_order": 1,
         "shift_name": "shift pagi",
         "schedule_in": "08:00",
         "schedule_out": "17:00",
         "break_start": "12:00",
         "break_end": "13:00"
       },
       {
         "pattern_order": 2,
         "shift_name": "shift siang",
         "schedule_in": "12:00",
         "schedule_out": "20:00",
         "break_start": "16:00",
         "break_end": "17:00"
       }
     ]
   }
   ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/webhooks/talenta/talenta-attendance-scheduler-changeshift
title: Attendance Scheduler Change Shift - Mekari Developers Documentation
---

# Attendance Scheduler Change Shift

## Event

```
talenta.attendance.scheduler.changeshift
```

## Schema

```
{
  "company_id": Number,
  "changes": [
    {
      "date": String,
      "employee_name": String,
      "employee_id":String,
      "user_id": Number,
      "old_shift": {
        "shift id": Number,
        "shift name": String,
        "schedule_in": String,
        "schedule_out": String,
        "break_start": String,
        "break_end": String
      },
      "new_shift": {
        "shift id": Number,
        "shift name": String,
        "schedule_in": String,
        "schedule_out": String,
        "break_start": String,
        "break_end": String
      }
    }
  ]
}
```

## Example Response

```
{
  "company_id": 1212,
  "changes": [
    {
      "date": "23-12-2024",
      "employee_name": "emp001",
      "employee_id": "asep",
      "user_id": 1212,
      "old_shift": {
        "shift id": 1231321,
        "shift name": "pagi",
        "schedule_in": "08:00",
        "schedule_out": "17:00",
        "break_start": "12:00",
        "break_end": "13:00"
      },
      "new_shift": {
        "shift id": 3213131,
        "shift name": "malam",
        "schedule_in": "17:00",
        "schedule_out": "23:00",
        "break_start": "20:00",
        "break_end": "21:00"
      }
    }
  ]
}
```

---



---
source: https://developers.mekari.com/docs/kb/changelog
title: Changelog - Mekari Developers Documentation
---

# Changelog

This changelog lists all additions and updates to the Mekari product API, in chronological order.

## February 23, 2025

Add API documentation for the [Mekari Expense](https://expense.mekari.com/) platform.

## Sep 18,2024

Java Documentation:

1. Add header `Accept` `application/json`- Add header `Content-Type` `application/json`- Declared JSON variable at Making API Request Section- Changed `<maven.compiler.source>` and `<maven.compiler.target>` to 1.8 since Java 8 is denoted as 1.8.- Corrected the missing closing tag `</dependencies>`.

## Sep 13,2024

* Update header Accept application/json HMAC Authentication for Node.js documentation.* Update header Accept application/json HMAC Authentication and add MEKARI\_API\_BASE\_URL in .env file for PHP documentation.

## June 14,2024

Adding Platform, [Klikpajak](https://klikpajak.id), Qontak, [Jurnal](https://jurnal.id) and Talenta webhooks documentation.

## June 07,2024

Updating webhook events documentation.

## February 26,2024

Adding [jurnal](https://jurnal.id) api docs, mekari pay service, kyc-backend api documentation.

## February 22, 2024

Adding Updates for Product APIs documentation (Qontak CRM and Qontak OmniChannel)

## December 12, 2023

Add support for query params if `request-line` header included on signature during HMAC Authentication process to enhance security protection during API authentication process. This means when generating the HMAC signature with `request-line` header, you need to add query params if the API URI has query param.

Previously if the full API URI is `POST https://api.mekari.com/v2/klikpajak/v1/efaktur/out?auto_approval=false`, the `request-line` will only contain method, path and http version. For example: `POST /v2/klikpajak/v1/efaktur/out HTTP/1.1`. However with this new changes, you must include the query params inside the `request-line`. For example: `POST /v2/klikpajak/v1/efaktur/out?auto_approval=false HTTP/1.1`. If you need help to verify the implementation you can always use [HMAC Validator](https://developers.mekari.com/dashboard/hmac-validator) to verify your signature is correct or not.

Support for `request-line` without query params is deprecated and we will drop the support by March 31st, 2023. We expect you made the changes on your application before March 31st, 2023.

---
