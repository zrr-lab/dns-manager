# CHANGELOG

## v0.1.2 (2025-03-30)

### ⬆️ deps

* ⬆️ deps: upgrade typer ([`2d791b6`](https://github.com/zrr-lab/dns-manager/commit/2d791b697baddc62fef69dcf612d3db0cd060fb4))

* ⬆️ deps: add pyright in dev deps ([`7a49a1f`](https://github.com/zrr-lab/dns-manager/commit/7a49a1f5d9f4664bd9c0917aa0118f5ad14f16f7))

### 🐛 fix

* 🐛 fix: support catch HTTPError ([`0ba7e68`](https://github.com/zrr-lab/dns-manager/commit/0ba7e6843471ea261d7961cec66d52ae973bfdc3))

### 👷 ci

* 👷 ci: add type check action ([`d849527`](https://github.com/zrr-lab/dns-manager/commit/d8495279b1e7970b10b09f867979142f5526b672))

### 📝 docs

* 📝 docs: update readme ([`a99a82c`](https://github.com/zrr-lab/dns-manager/commit/a99a82c3a3fceba474ae6c14704ed78371b5af97))

## v0.1.1 (2024-11-04)

### ✅ test

* ✅ test: add e2e test ([`60f5a5d`](https://github.com/zrr-lab/dns-manager/commit/60f5a5d363d68d1575b83264c8e19f2225f71c1b))

### ⬆️ deps

* ⬆️ deps: upgrade typer to 0.12.0 ([`4f3e303`](https://github.com/zrr-lab/dns-manager/commit/4f3e3039816217a9b25d95d531e73b3d4f7b7164))

### 🐛 fix

* 🐛 fix: fix error when ~/.config/dns-manager does not exist (#3)

* 🐛 fix: fix error when `~/.config/dns-manager` does not exist

* 🐛 fix: fix action ([`955fea8`](https://github.com/zrr-lab/dns-manager/commit/955fea8d5eb5e84fc8cb21537d09f85bb65ceea8))

### 👷 ci

* 👷 ci: update test and release ([`476c97b`](https://github.com/zrr-lab/dns-manager/commit/476c97b9b2c5137a52d33ce83d5107c670c6a90a))

* 👷 ci: update runs-on to 22.04 ([`5327d3e`](https://github.com/zrr-lab/dns-manager/commit/5327d3e851a4b19469bcd407d1ab6dc5709a2c91))

* 👷 ci: add release action ([`902592e`](https://github.com/zrr-lab/dns-manager/commit/902592e6c82351cbf6b150bed91043ab2facde66))

* 👷 ci: add codespeed and more actions ([`26ada52`](https://github.com/zrr-lab/dns-manager/commit/26ada52aebd4523b85566d356c31844a3166d8f7))

### 📝 docs

* 📝 docs: update readme ([`e31d46a`](https://github.com/zrr-lab/dns-manager/commit/e31d46a4d21a235c05e73c1a5b3e06a6554e252c))

### 📦 build

* 📦 build: use uv instead of pdm ([`84ef2be`](https://github.com/zrr-lab/dns-manager/commit/84ef2be72f54597844c749015df0cfe8253c4afd))

* 📦 build: use uv instead of pdm ([`0b80ed7`](https://github.com/zrr-lab/dns-manager/commit/0b80ed7c6819497a28dfc537f7fc5ba7511eb5fb))

## v0.1.0 (2024-07-15)

### 🐛 fix

* 🐛 fix: SnmpGetter use default route ip ([`2cc1f4f`](https://github.com/zrr-lab/dns-manager/commit/2cc1f4f296937d5313edac875b006983e1a41545))

## v0.0.15 (2024-06-01)

### ♻️ refactor

* ♻️ refactor: add exception process in LexiconSetter ([`dd085ff`](https://github.com/zrr-lab/dns-manager/commit/dd085ff16097286110dfb7da0bdbfcc75f23b9fc))

### ✨ feat

* ✨ feat: add lexicon setter ([`d6ed1bb`](https://github.com/zrr-lab/dns-manager/commit/d6ed1bb9b745a3f4f11fd152c8819a31952a21f5))

### 🐛 fix

* 🐛 fix: fix env in ci ([`b684bd5`](https://github.com/zrr-lab/dns-manager/commit/b684bd5c963cfac62fe8e16806fb02a9e22a76ad))

* 🐛 fix: fix ci ([`571c665`](https://github.com/zrr-lab/dns-manager/commit/571c665884c5d008d8726d668e34a85a12b93168))

## v0.0.14 (2024-04-16)

### 👷 ci

* 👷 ci: update action-gh-release to v2 ([`6814e5a`](https://github.com/zrr-lab/dns-manager/commit/6814e5a8898b0d14217a3d40957a1a1d180fffb4))

## v0.0.13 (2024-04-09)

### ➕ deps

* ➕ deps: add some necessary deps ([`0c75a91`](https://github.com/zrr-lab/dns-manager/commit/0c75a91a42ec9c5f7944cf8a1474867a5a4b9262))

### ⬆️ deps

* ⬆️ deps: upgrade auto-token ([`ed5f686`](https://github.com/zrr-lab/dns-manager/commit/ed5f686af06b98c6ad521c84a3801aaeb81262b5))

### 🐛 ci

* 🐛 ci: fix release action ([`3f16228`](https://github.com/zrr-lab/dns-manager/commit/3f1622898fdaad5029f3706ecca9d6f9953b2735))

### 🐛 fix

* 🐛 fix: fix get_token in create_setter_by_str ([`374f70a`](https://github.com/zrr-lab/dns-manager/commit/374f70abe987ff4f0e6cde56dbf82d7aaa852576))

* 🐛 fix: fix actions and justfile ([`d1f2f2c`](https://github.com/zrr-lab/dns-manager/commit/d1f2f2cedab06d3f077f23ed57aa91b8bc6d1edb))

* 🐛 fix: fix justfile ([`4075274`](https://github.com/zrr-lab/dns-manager/commit/40752748b1e6cef7b844019369c4e073e061758a))

### 👷 ci

* 👷 ci: imporve actions and add justfile ([`251941f`](https://github.com/zrr-lab/dns-manager/commit/251941f57352c5225357ccbb204f966cbb997406))

### 📌 deps

* 📌 deps: update lockfile ([`f8cd94d`](https://github.com/zrr-lab/dns-manager/commit/f8cd94d6c0359c31b9ada9b5bb1d6c3d908caedd))

## v0.0.12 (2024-04-08)

### ♻️ refactor

* ♻️ refactor: improve Setter ([`d746a9d`](https://github.com/zrr-lab/dns-manager/commit/d746a9d7d5e95097847135a169a03b0be55fa06f))

### ✨ feat

* ✨ feat: add ignored_records, add remove_unmanaged args, support records_files ([`7b37486`](https://github.com/zrr-lab/dns-manager/commit/7b37486f79161dd93939c9689cd88f0d7dd3bcce))

### 🎨 style

* 🎨 style: change line-length to 100 ([`ac93311`](https://github.com/zrr-lab/dns-manager/commit/ac933112e6a8c364cf6d89f234a1c65fe6dbde2f))

### 👷 ci

* 👷 ci: fix release ([`7a9d566`](https://github.com/zrr-lab/dns-manager/commit/7a9d566db4f6847bdc373467773daa4d3177d9d7))

## v0.0.11 (2024-03-17)

### 🧹 chore

* 🧹 chore: remove python version 3.9 from build matrix ([`06c1510`](https://github.com/zrr-lab/dns-manager/commit/06c15103b8d209ed273e85d293d7b22e0360aeae))

## v0.0.10 (2024-03-13)

### 🐛 fix

* 🐛 fix: update python version requirement in pdm.lock and pyproject.toml files ([`22b4f1a`](https://github.com/zrr-lab/dns-manager/commit/22b4f1a9138b1345e76532044aab1f529ab0a2aa))

### 🧹 chore

* 🧹 chore: update gitignore, dns_manager/getter/snmp.py, and pdm.lock files ([`1b9903b`](https://github.com/zrr-lab/dns-manager/commit/1b9903b17b1e58131042d14904f4875b38f9ebf3))

## v0.0.9 (2024-02-23)

### ♻️ refactor

* ♻️ refactor: change deault config path ([`23386a5`](https://github.com/zrr-lab/dns-manager/commit/23386a50876147aeaba896bf2c132493cfebf71f))

## v0.0.8 (2024-02-23)

### ♻️ refactor

* ♻️ refactor: rename to dns-manager ([`77c6690`](https://github.com/zrr-lab/dns-manager/commit/77c6690755681f6be1805bab58570ccab4feecf5))

### ✏️ fix

* ✏️ fix: fix some name ([`df271a7`](https://github.com/zrr-lab/dns-manager/commit/df271a7c4d4ff73a6b0102c33175c1855ccf7d0e))

## v0.0.7 (2024-02-20)

### ✨ feat

* ✨ feat: support public in config ([`eb80c3a`](https://github.com/zrr-lab/dns-manager/commit/eb80c3a6c56b0f866fa9ee68f41d5de4d51aac25))

* ✨ feat: add public getter ([`f237774`](https://github.com/zrr-lab/dns-manager/commit/f237774c024e2eb97e0eb8abafe0a81a6f546f53))

## v0.0.6 (2024-02-11)

### ♻️ refactor

* ♻️ refactor: use auto-token ([`83ea4ee`](https://github.com/zrr-lab/dns-manager/commit/83ea4ee737bd7d131c76b774f648d8aa7b03d921))

### ✨ feat

* ✨ feat: support yaml and toml ([`0912697`](https://github.com/zrr-lab/dns-manager/commit/0912697b470746bc1eb13fc356d055ae2f506d0f))

* ✨ feat: support multi subdomain ([`9cfa371`](https://github.com/zrr-lab/dns-manager/commit/9cfa371426a2b857cb8af1bebe06fbc94b148127))

### ⬆️ deps

* ⬆️ deps: update ([`a090c94`](https://github.com/zrr-lab/dns-manager/commit/a090c94c7403d5271853d59c23e0fd4f233e91bd))

## v0.0.5 (2024-01-19)

### Unknown

* 🎨 format: use F ([`1b3ef7b`](https://github.com/zrr-lab/dns-manager/commit/1b3ef7bcfe6fe7fc86bd0d5fc075acaee24c0227))

* ✅ tests: update test ([`01fc60c`](https://github.com/zrr-lab/dns-manager/commit/01fc60cec1bec66d415aa165835575368a6bc33d))

### ♻️ refactor

* ♻️ refactor: improve getter ([`777bc9c`](https://github.com/zrr-lab/dns-manager/commit/777bc9ce8ea3907fd3a7a8e428eaf9d0bf7c391b))

* ♻️ refactor: use setter and getter dir name ([`25449ab`](https://github.com/zrr-lab/dns-manager/commit/25449abc5216fc6304810910345b4cd6920f36a2))

* ♻️ refactor: mv update_records functions to utils ([`37bec9e`](https://github.com/zrr-lab/dns-manager/commit/37bec9e39c79e62b2139adf9e8c56189fac7acc0))

* ♻️ refactor: impl IPGetter and DNSSetter ([`6ed9280`](https://github.com/zrr-lab/dns-manager/commit/6ed9280820301eaf8697777074c4a4e2d1874482))

* ♻️ refactor: improve Client and get_interface_ip ([`2457148`](https://github.com/zrr-lab/dns-manager/commit/2457148ddce729ce2fc2c0befc7e54a372c0b1a6))

### ✅ test

* ✅ test: add classify_record test ([`40347cd`](https://github.com/zrr-lab/dns-manager/commit/40347cdbb92a334f7fa3e3cedc79eec935f92cc1))

### ✨ feat

* ✨ feat: add countdown in daemon ([`1bdffb9`](https://github.com/zrr-lab/dns-manager/commit/1bdffb9dab2de4b691353e2f0ead6b1c0c25f5ba))

* ✨ feat: add RecordStatus and more clear logs ([`dd8ee12`](https://github.com/zrr-lab/dns-manager/commit/dd8ee12bdc238d063c13e6050e056d9c447d277f))

* ✨ feat: support watch config in  daemon command ([`bb1d129`](https://github.com/zrr-lab/dns-manager/commit/bb1d129c907953f39555ae19a20ce64e6bbb576b))

* ✨ feat: add daemon ([`9921470`](https://github.com/zrr-lab/dns-manager/commit/992147067d356c39b77be8fdc3c469195abb29a9))

* ✨ feat: support secret env ([`54093b7`](https://github.com/zrr-lab/dns-manager/commit/54093b70e4f98ab034d0b815678f56d4834e8a4a))

* ✨ feat: add delete_record ([`f08ab80`](https://github.com/zrr-lab/dns-manager/commit/f08ab8064128289f5f5757ac759fbcdd148ff192))

### 🎨 style

* 🎨 style: add more ruff rules ([`71ced1a`](https://github.com/zrr-lab/dns-manager/commit/71ced1a5d0e9aeae9808e10894834a5bf2d66bb5))

### 🐛 fix

* 🐛 fix: fix CNAME ([`3316ee7`](https://github.com/zrr-lab/dns-manager/commit/3316ee76a76134d53984e4c9fce44e44065a3c67))

* 🐛 fix: fix record cache ([`24f6a75`](https://github.com/zrr-lab/dns-manager/commit/24f6a75b4b855897fdb987b8af898a8a0a5cd7e6))

* 🐛 fix: fix generate_record ([`d6165dd`](https://github.com/zrr-lab/dns-manager/commit/d6165dd87253bbca2d7e63e83bfe3c67400be0e6))

* 🐛 fix: makedir when token dir is not exsited ([`218483d`](https://github.com/zrr-lab/dns-manager/commit/218483d67e47f12cb7ab95d14b924ba972e758bb))

* 🐛 fix: add pyparsing dep ([`da2d3be`](https://github.com/zrr-lab/dns-manager/commit/da2d3be2cdb313e7b6a281557da7c9d88c2dd2e3))

### 👷 ci

* 👷 ci: add SECRET ([`620f56d`](https://github.com/zrr-lab/dns-manager/commit/620f56d73103bac2c432497de11f476da3e0814e))

* 👷 ci: add publish release ([`83113aa`](https://github.com/zrr-lab/dns-manager/commit/83113aa4e99017df239bef33ae402ca015836b30))

* 👷 ci: improve publish workflow ([`5202403`](https://github.com/zrr-lab/dns-manager/commit/520240350114db12fd66570951417c8fa4ca1bf8))

### 💄 style

* 💄 style: improve log ([`53785f5`](https://github.com/zrr-lab/dns-manager/commit/53785f5e0ac66315638dfceed24b2a37fc3f8784))

* 💄 style: improve colors ([`8448694`](https://github.com/zrr-lab/dns-manager/commit/84486942136687fedfdbc3a7afbe229f1f431f89))

### 📌  deps

* 📌  deps: pin deps ([`290b364`](https://github.com/zrr-lab/dns-manager/commit/290b3644b6cb80066659148dd50215df02c8a0d2))

### 🔧 chore

* 🔧 chore(config): Remove some unused pdm build config ([`08883f3`](https://github.com/zrr-lab/dns-manager/commit/08883f33c868e5b40df663d965ab5132a63e82c5))

## v0.0.4 (2023-11-30)

### Unknown

* improve code ([`d69036a`](https://github.com/zrr-lab/dns-manager/commit/d69036ab560b3e87a63ef3c022f296fa9084ea19))

## v0.0.3 (2023-11-30)

### Unknown

* add pyfuture ([`591528a`](https://github.com/zrr-lab/dns-manager/commit/591528a1cd28b83a75a8d85a6a7756df9723c223))

## v0.0.2 (2023-11-28)

### Unknown

* improve log and fix bug ([`f14b243`](https://github.com/zrr-lab/dns-manager/commit/f14b2437b85a862b060819c1f363a72408a5b056))

## v0.0.1 (2023-11-27)

### Unknown

* format ([`84d2eaf`](https://github.com/zrr-lab/dns-manager/commit/84d2eaf69638281934d14101fc5d4c099751c1e6))

* rename to auto-ddns ([`73b9df8`](https://github.com/zrr-lab/dns-manager/commit/73b9df8ccdf909c5acc8b552ca44d900bddfdb3f))

* add coverage and publish workflows ([`82fc6ad`](https://github.com/zrr-lab/dns-manager/commit/82fc6addfb9fc3b9516367b485683d5992e2336d))

* init ([`9cd325e`](https://github.com/zrr-lab/dns-manager/commit/9cd325e53db655ac7fd76bb5de2ac92b02a506a4))
