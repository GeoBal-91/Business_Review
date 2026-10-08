# Frozen-module integrity

Baseline: the current extracted Desktop/V9_Beta1_1 folder. Its data_pipeline.py and store_status.py already contain the finalized partial-uptime fix absent from the ZIP. Neither file changed in Beta2. The extracted default SBU is JEWELRY.

PASS: scoring.py, store_status.py, data_pipeline.py, analysis.py, coverage_guard.py, triage_config.py and formatting.py are byte-identical. All config analytical constants/settings are AST-identical; only the module description and output filename changed. business_classification.py is AST-identical after normalizing the sole release-version literal.

Nine independent baseline replays, including the 80-store golden fixture, match exactly across stores, metrics, opportunities, actions, reviews and V2.1 store classifications. Existing golden scoring values were not regenerated.

| File | Baseline SHA-256 | Beta2 SHA-256 | Identical |
|---|---|---|---|
| analysis.py | 7d6faba3bbd92ebbaf6bdfcbfb40a41e0a40d5fefdc01015275ae28840cd455b | 7d6faba3bbd92ebbaf6bdfcbfb40a41e0a40d5fefdc01015275ae28840cd455b | True |
| beta_presentation.py | 2ec508df12230570b2312240963928d9986ee5f46951cee24b3def82b576b5a7 | 4739b0a8a3c2ec5ce581b91ccf50f35e388455464d75eb1b3522904136c280b3 | False |
| beta_validation.py | a1daaf5097b53a53f4b5250eb0079599ddf54a0ebafb001287dd66f89c0d0e95 | 50b88cf0be8544d308d41c0ec4142ae728a2ea1f6c6a8a2db728dcd406d39699 | False |
| business_classification.py | 4c01bbd09c6793d9690410a3c8fca6f6e5a1e42a4d06a50bc21e15cef44bc5c5 | b8a0537cce0ee6841435f96ccd410e0c9d29f4c9f1d9047210592e3fe2acdf29 | False |
| config.py | fcd99003b6364213700b2ecf368a9f915bae014218fd435e28ae1f450b975b7a | 8a5a1ec46c5a85b6b1862eb27f487bbcce5158c9646f924d0614b987dde2a678 | False |
| coverage_guard.py | 010a3f9bd6bcd7a7abdb91248e22f650a49dd4b373cd61990dc8ac2e0f1a7819 | 010a3f9bd6bcd7a7abdb91248e22f650a49dd4b373cd61990dc8ac2e0f1a7819 | True |
| data_pipeline.py | 07ee42f82d46c1e38409ef30703e9968cca95ab4a667c6cc1f0f17420a373b9e | 07ee42f82d46c1e38409ef30703e9968cca95ab4a667c6cc1f0f17420a373b9e | True |
| diagnostics.py | 1731e869b59a19d29fb3e9e0b297d27afb0729804258b925231761dbbd11fab5 | 1731e869b59a19d29fb3e9e0b297d27afb0729804258b925231761dbbd11fab5 | True |
| formatting.py | 762cfc9bcbeef2a0a2152e21b3be2d40f86fedf81bbc06be41b50c23636d6c1f | 762cfc9bcbeef2a0a2152e21b3be2d40f86fedf81bbc06be41b50c23636d6c1f | True |
| main.py | 0ff324221dd09a47f07760dd3ed460e45598051ece91b28e706ee30ab94de532 | dd7f68f2aa5e631e331c959d82dac26781e563abbbde700aa8ff8d34c899972a | False |
| main_v2_1.py | 0524a6bb08bfcf2d08e08f4a26dea0d01bd2b377cbb416c7abab1e3a5b627ef7 | bdb96dba39e298d8050160050f291db52216c3f45fc6b7a82618b6ac69b61e34 | False |
| ppt_core.py | 25c77e7665a6477e6fbfab0ab02af9ab815d6f8977a678118826469ad13e3464 | 25c77e7665a6477e6fbfab0ab02af9ab815d6f8977a678118826469ad13e3464 | True |
| presentation.py | d1229bd38ce071f4cc2faee8ec52ba939a09ad07551ae0cedc4d2cd4067940c9 | 95d961f1e3015f897bc73b71dbe62341e6e7ab2c441532b5d4ed7f7234ab4416 | False |
| presentation_hardening.py | 063a7c801b4b87047ef1c6f2eda266655d45af3bf8c3d128f1a033e1d7711425 | 01052ab4e651210cec49983bfc77075b07541351b1955a576f48f1e6e4290073 | False |
| presentation_polish.py | 7f20120334eafbbc5deb20c6f89a68cce4ebe1e31f5cc964b9f6a7e912e9f2da | a548e6940d0036be924c5c68c6c20b76ac8986084ce1c745f60560fd04c8c1de | False |
| scoring.py | 902b8dcbe73d547613d0b2a0d411d286f3a667aaa775fa2da8d121ca3ff32aa8 | 902b8dcbe73d547613d0b2a0d411d286f3a667aaa775fa2da8d121ca3ff32aa8 | True |
| slides_market.py | c5eb9b8f4a27122585fbe72a19cd32924eba759a5f1a1e80b41a252cccc4eb79 | c5eb9b8f4a27122585fbe72a19cd32924eba759a5f1a1e80b41a252cccc4eb79 | True |
| slides_partner.py | 0417b4281fcb76cad82cedc6c1820e90904c16e3ca415a7af96e101ae7b62efa | 0417b4281fcb76cad82cedc6c1820e90904c16e3ca415a7af96e101ae7b62efa | True |
| slides_stores.py | 4b118c80dc63247f5655828809e1cdde5756b0b9e951f599ac27546aaf7c8355 | 4b118c80dc63247f5655828809e1cdde5756b0b9e951f599ac27546aaf7c8355 | True |
| store_status.py | ab016f99fe1b9fa6435995d4d40c6fae98ab063bb930e84c9856feda62155124 | ab016f99fe1b9fa6435995d4d40c6fae98ab063bb930e84c9856feda62155124 | True |
| theme.py | 94d6f7a2ffc1fbb7281367812ce4c43a9dc1aeab1a75b1b7479a2fd1ad6059a5 | 94d6f7a2ffc1fbb7281367812ce4c43a9dc1aeab1a75b1b7479a2fd1ad6059a5 | True |
| triage_config.py | d81933908220bf233eab5ada4c8a3db31c120775a3f7ab3a591771e3f5988a3c | d81933908220bf233eab5ada4c8a3db31c120775a3f7ab3a591771e3f5988a3c | True |
| triage_exports.py | c849ef99449fb866bd8a5e1670da1b70fae4cf9f2e03f0e527940be125987793 | 51b173008438c2f1a2bc03f3c4fe0130d3359d00bd452b62b6611e3fc7c29a6c | False |
| triage_presentation.py | 5ffc85407859efae3bc18688bd528e3f93d88b764f668cad28327c80de7b4106 | 428d4e311e48635e228e001bcf12e71bce2cd3b8dd74f124d3ab62ec59f0690d | False |
| validate.py | dcd3ea89b87efe4aa1f2a6e96ace278c77f86dfe620084b37092f8c47b9fa5df | dcd3ea89b87efe4aa1f2a6e96ace278c77f86dfe620084b37092f8c47b9fa5df | True |
