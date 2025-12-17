# Changelog

## 0.9.0 (2025-12-14)

Full Changelog: [v0.8.0...v0.9.0](https://github.com/limrun-inc/python-sdk/compare/v0.8.0...v0.9.0)

### Features

* **api:** add android sandbox api ([b1ec65b](https://github.com/limrun-inc/python-sdk/commit/b1ec65b1d7e36768d2bf3c8627242cc889f143ec))
* **api:** add asset type configuration with chrome flag ([0900df2](https://github.com/limrun-inc/python-sdk/commit/0900df2b560b981493c0c1572b5dcca043b7524a))
* **api:** add the optional errorMessage field in status ([6d26c2b](https://github.com/limrun-inc/python-sdk/commit/6d26c2bdedd6f9e576fd9419022d150dbdb3194f))
* **api:** make chromeFlag enum with supported value ([a937aac](https://github.com/limrun-inc/python-sdk/commit/a937aac4d9c69a21886f5c477e989edbbbaf9732))
* **api:** manual updates ([57c22b4](https://github.com/limrun-inc/python-sdk/commit/57c22b43395e906b6a2a869e7355fe1938770796))
* **api:** manual updates ([f88a368](https://github.com/limrun-inc/python-sdk/commit/f88a36818071f20c4a4b06df26a25ee6e0ab0b9d))


### Bug Fixes

* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([bd4bed9](https://github.com/limrun-inc/python-sdk/commit/bd4bed99a71cc69b225adc7c8bd0439a288e0b34))
* ensure streams are always closed ([63f1ee4](https://github.com/limrun-inc/python-sdk/commit/63f1ee4d81c796f3d0aa061726b8a542b6862a0c))
* **types:** allow pyright to infer TypedDict types within SequenceNotStr ([08396f0](https://github.com/limrun-inc/python-sdk/commit/08396f04ff54737c4d9f9b7da4c37aa1f8620537))


### Chores

* add Python 3.14 classifier and testing ([e635bb6](https://github.com/limrun-inc/python-sdk/commit/e635bb6f3c9930eb22551f692062bd9e45837c36))
* **deps:** mypy 1.18.1 has a regression, pin to 1.17 ([5469100](https://github.com/limrun-inc/python-sdk/commit/54691000d4ca3460ead03628d6d2d3a4a4ffea17))
* **docs:** use environment variables for authentication in code snippets ([af6c346](https://github.com/limrun-inc/python-sdk/commit/af6c346ea2fdbce9e207e59d829253a0617fced6))
* update lockfile ([bd03e1b](https://github.com/limrun-inc/python-sdk/commit/bd03e1ba15189503e3617b052701e7ed69b9e7a2))

## 0.8.0 (2025-11-11)

Full Changelog: [v0.7.0...v0.8.0](https://github.com/limrun-inc/python-sdk/compare/v0.7.0...v0.8.0)

### Features

* **api:** add assetId as asset source kind ([1aac770](https://github.com/limrun-inc/python-sdk/commit/1aac770249a41d2ceb6147cbe04cddf92ba23bbb))
* **api:** add comma-separated state for multi-state listings ([58b65a2](https://github.com/limrun-inc/python-sdk/commit/58b65a2e1c2a4970f480ac65b54e6408ecb981ce))
* **api:** add pagination for ios instances and assets as well ([123d228](https://github.com/limrun-inc/python-sdk/commit/123d2288130547b7e69f89cc9977e82baf813bee))
* **api:** add pagination to asset spec ([8be229c](https://github.com/limrun-inc/python-sdk/commit/8be229c8d4514cd2c033fe9cbb78221f14c64206))
* **api:** add reuseIfExists to creation endpoint ([4a0dd43](https://github.com/limrun-inc/python-sdk/commit/4a0dd43c17e8750e60f588e4fb2985d195daaa58))
* **api:** disable pagination for assets ([4b449fa](https://github.com/limrun-inc/python-sdk/commit/4b449fabb5b50dc0b3aea34a30f0ca0c29e26bb7))
* **api:** enable pagination for android_instances ([04130ef](https://github.com/limrun-inc/python-sdk/commit/04130ef1ab28bb6db9bef0727598c0c01950a3c3))
* **api:** manual updates ([52753ed](https://github.com/limrun-inc/python-sdk/commit/52753ed8cd09c24370aa3665e8310fefe7376562))
* **api:** manual updates ([e616c29](https://github.com/limrun-inc/python-sdk/commit/e616c29a6e3addbeab4788734dee903300a72b82))
* **api:** move pagination prop to openapi ([2d59a37](https://github.com/limrun-inc/python-sdk/commit/2d59a37ab0f2663a389ce65a1fba113ef5700720))
* **api:** regenerate new pagination fields ([83ff598](https://github.com/limrun-inc/python-sdk/commit/83ff598ecde93383f846fe55605633bfa744762a))
* **api:** update comment ([e6e7657](https://github.com/limrun-inc/python-sdk/commit/e6e7657d1a32dbde27a9fcaa3408e9b327432fe2))
* **api:** update to use LIM_API_KEY instead of LIM_TOKEN ([ba2e85e](https://github.com/limrun-inc/python-sdk/commit/ba2e85e00e7ee937ab8ceaf5f9119a7a4f74b49a))


### Bug Fixes

* compat with Python 3.14 ([c97037d](https://github.com/limrun-inc/python-sdk/commit/c97037dc5c683fcc72c5ce50b58ba1ee7951432a))


### Chores

* **package:** drop Python 3.8 support ([3be5696](https://github.com/limrun-inc/python-sdk/commit/3be5696b0cf40c1f02467d03e85c0181667fb9ea))

## 0.7.0 (2025-11-05)

Full Changelog: [v0.6.0...v0.7.0](https://github.com/limrun-inc/python-sdk/compare/v0.6.0...v0.7.0)

### Features

* **api:** add asset deletion endpoint ([e468855](https://github.com/limrun-inc/python-sdk/commit/e4688552f9edac991e15e0e3c9e052882b7c8e5f))
* **api:** add ios port-forward endpoint url to return type ([a636183](https://github.com/limrun-inc/python-sdk/commit/a6361831f2965f40dca0304c2a6a9b774b54a938))
* **api:** add launchMode to iOS asset object ([4e5bb3c](https://github.com/limrun-inc/python-sdk/commit/4e5bb3c6727312a6e2006d4a323685eeecd3344a))
* **api:** add the assigned state to both android and ios instance states ([0aa0e44](https://github.com/limrun-inc/python-sdk/commit/0aa0e4428f16befa8058ddaa81c432336b9ab621))


### Bug Fixes

* **client:** close streams without requiring full consumption ([f2fe77c](https://github.com/limrun-inc/python-sdk/commit/f2fe77cfdb1027a3bde5fe2ddfa763598ead2194))


### Chores

* **internal/tests:** avoid race condition with implicit client cleanup ([73d9600](https://github.com/limrun-inc/python-sdk/commit/73d960047c072bc1139fdbb2fdc7d8c8b844cdb4))
* **internal:** grammar fix (it's -&gt; its) ([7e8562b](https://github.com/limrun-inc/python-sdk/commit/7e8562bce0d40d2e239132d7fd9d0d5b1e8ee5a8))

## 0.6.0 (2025-10-29)

Full Changelog: [v0.5.0...v0.6.0](https://github.com/limrun-inc/python-sdk/compare/v0.5.0...v0.6.0)

### Features

* **api:** add explicit pagination fields ([c4756f3](https://github.com/limrun-inc/python-sdk/commit/c4756f391ef5094ffccd2988e49ae2fc2be3fe62))
* **api:** add os version clue ([7d0bda5](https://github.com/limrun-inc/python-sdk/commit/7d0bda58126acff22bf569828ea1c38abf144e0c))
* **api:** limit pagination only to limit parameter temporarily ([68a99e1](https://github.com/limrun-inc/python-sdk/commit/68a99e16648bd03a5edaebd4115b77fd5ab311f7))
* **api:** manual updates ([6301238](https://github.com/limrun-inc/python-sdk/commit/6301238cfadf4c89827fee3e2ecca0194b3e5b50))
* **api:** manual updates ([6dda9e7](https://github.com/limrun-inc/python-sdk/commit/6dda9e73f01b3cc6be13633b1a6f84bd4477ce18))
* **api:** os version description to show possible values ([a4d9cd3](https://github.com/limrun-inc/python-sdk/commit/a4d9cd3c2b77d85c010e0a9884b7aac36136e354))
* **api:** osVersion clue is available only in Android yet ([545f2db](https://github.com/limrun-inc/python-sdk/commit/545f2dbb4ce59f7288fa978df60b2b46a6ac8736))
* **api:** remaining pieces of pagionation removed temporarily ([73713dd](https://github.com/limrun-inc/python-sdk/commit/73713dd432d23023862e4d15a609c8ea4fdd9819))
* **api:** update assets and ios_instances endpoints with pagination ([95668d7](https://github.com/limrun-inc/python-sdk/commit/95668d74ca87e07403623c3a3ddcb93fa42820d6))
* **api:** update stainless schema for pagination ([3767bd6](https://github.com/limrun-inc/python-sdk/commit/3767bd695bef605b8d2169d4bb783864df90401f))


### Chores

* bump `httpx-aiohttp` version to 0.1.9 ([ce7151e](https://github.com/limrun-inc/python-sdk/commit/ce7151eb8db959e77260d8da78343c91b7a36853))
* **internal:** detect missing future annotations with ruff ([5ea3e8e](https://github.com/limrun-inc/python-sdk/commit/5ea3e8e2ce8f057a8e22854221db80b5f8aa229c))

## 0.5.0 (2025-10-07)

Full Changelog: [v0.4.0...v0.5.0](https://github.com/limrun-inc/python-sdk/compare/v0.4.0...v0.5.0)

### Features

* **api:** add the new multiple apk installation options ([58e81cc](https://github.com/limrun-inc/python-sdk/commit/58e81cc2074ef7a75dcc8ac25f50a0b2bf0f3c57))
* **api:** mark public urls as required ([0af09f5](https://github.com/limrun-inc/python-sdk/commit/0af09f54ee37d7b4cfe3d4b02d69faf412cf2442))
* **api:** revert api change ([5be7d22](https://github.com/limrun-inc/python-sdk/commit/5be7d225f832016734c449ba2fd6c906efd9646c))


### Chores

* do not install brew dependencies in ./scripts/bootstrap by default ([a810b55](https://github.com/limrun-inc/python-sdk/commit/a810b55f4f433cf81e91cc6384eb803d9178b75e))
* **internal:** update pydantic dependency ([21a183f](https://github.com/limrun-inc/python-sdk/commit/21a183f72ff7e281b0db44cd1f598fd7f73bffa9))
* **types:** change optional parameter type from NotGiven to Omit ([200fa8d](https://github.com/limrun-inc/python-sdk/commit/200fa8ddfca76d214e1b8c793ef5939a629d1b30))

## 0.4.0 (2025-09-12)

Full Changelog: [v0.3.0...v0.4.0](https://github.com/limrun-inc/python-sdk/compare/v0.3.0...v0.4.0)

### Features

* **api:** manual updates ([7dbb780](https://github.com/limrun-inc/python-sdk/commit/7dbb780b65eae748a19c41154d41b4f24c153bd1))
* **api:** manual updates ([3836853](https://github.com/limrun-inc/python-sdk/commit/38368531d480706c4528c6bd0b4b94a94e788592))

## 0.3.0 (2025-09-11)

Full Changelog: [v0.2.0...v0.3.0](https://github.com/limrun-inc/python-sdk/compare/v0.2.0...v0.3.0)

### Features

* **api:** remove md5filter from list assets ([9e460d4](https://github.com/limrun-inc/python-sdk/commit/9e460d4e032d1549f0fb419bb871fd03a846f864))

## 0.2.0 (2025-09-09)

Full Changelog: [v0.1.1...v0.2.0](https://github.com/limrun-inc/python-sdk/compare/v0.1.1...v0.2.0)

### Features

* **api:** manual updates ([9c3f233](https://github.com/limrun-inc/python-sdk/commit/9c3f2330f50cdeef71004c7ea10874cc4fc157d3))


### Chores

* update SDK settings ([eef22eb](https://github.com/limrun-inc/python-sdk/commit/eef22eba5f9ee08a1620cf7155306f01b9c0020c))

## 0.1.1 (2025-09-09)

Full Changelog: [v0.1.0...v0.1.1](https://github.com/limrun-inc/python-sdk/compare/v0.1.0...v0.1.1)

### Chores

* update SDK settings ([e1a6a95](https://github.com/limrun-inc/python-sdk/commit/e1a6a95be568d7fd21fcbfeba3460b2934e84212))

## 0.1.0 (2025-09-08)

Full Changelog: [v0.0.1...v0.1.0](https://github.com/limrun-inc/python-sdk/compare/v0.0.1...v0.1.0)

### Features

* **api:** manual updates ([77b548c](https://github.com/limrun-inc/python-sdk/commit/77b548ca5977d8155954a4ad2da14086ef66de59))


### Chores

* configure new SDK language ([2c6c2f5](https://github.com/limrun-inc/python-sdk/commit/2c6c2f56099811070dc4c137f4cdbad18ec5c5a6))
* update SDK settings ([905181c](https://github.com/limrun-inc/python-sdk/commit/905181c229934fd82579ea0364b5d34f05b89138))
