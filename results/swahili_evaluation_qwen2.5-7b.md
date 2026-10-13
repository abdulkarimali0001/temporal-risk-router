# Swahili questions

Model `qwen2.5:7b` · 2026-10-10 · 32 Swahili questions (answers verified 2026-10-09). Search: Wikipedia + live web.

| Method | Correct | Wrong | No guess | Searched |
|---|---|---|---|---|
| Memory only | 9/32 (28%) | 23 | 0 | 0 |
| Search: English Wikipedia only | 20/32 (62%) | 11 | 1 | 32 |
| Search: own language + English | 25/32 (78%) | 7 | 0 | 32 |
| Router (both checks) | 26/32 (81%) | 6 | 0 | 26 |

| Question type | n | Memory only | Search: English Wikipedia only | Search: own language + English | Router (both checks) |
|---|---|---|---|---|---|
| General knowledge | 10 | 7/10 | 7/10 | 7/10 | 8/10 |
| Local / rare facts | 10 | 0/10 | 3/10 | 8/10 | 8/10 |
| Changes over time | 12 | 2/12 | 10/12 | 10/12 | 10/12 |

## Wrong answers

- **Memory only**, sw03 Ziwa kubwa zaidi barani Afrika ni lipi? (expected Victoria): Barani Afrika ni lipi kubwa zaidi kwa Uganda.
- **Search: English Wikipedia only**, sw03 Ziwa kubwa zaidi barani Afrika ni lipi? (expected Victoria): Ziwa kubwa zaidi barani Afrika ni Greenland [1].
- **Memory only**, sw08 Tanzania hutumia sarafu gani? (expected shilingi): Tanzania hutumia sarafu ya kiswahili kusaidia kufikia ujuzi wa ujenzi wa kijamii na kutoa nyaraka zaidi zinazopendekezwa.
- **Search: own language + English**, sw08 Tanzania hutumia sarafu gani? (expected shilingi): Tanzania hutumia dola ya Marekani kama sarafu yao rasmi [1].
- **Router (both checks)**, sw08 Tanzania hutumia sarafu gani? (expected shilingi): Tanzania hutumia dola ya Marekani kama sarafu yao rasmi [1].
- **Search: English Wikipedia only**, sw09 Kisiwa cha Unguja kinajulikana pia kwa jina gani? (expected Zanzibar): Kisiwa cha Unguja kinajulikana pia kwa jina "Unguja Island" [2].
- **Search: own language + English**, sw09 Kisiwa cha Unguja kinajulikana pia kwa jina gani? (expected Zanzibar): Kisiwa cha Unguja kinajulikana pia kwa jina "Unguja". [6]
- **Memory only**, sw10 Mto mrefu zaidi duniani ni upi? (expected Nile): Mto mrefu zaidi duniani ni Amazon mrefu.
- **Search: English Wikipedia only**, sw10 Mto mrefu zaidi duniani ni upi? (expected Nile): Mto mrefu mpya duniani ni Amazon River [2].
- **Search: own language + English**, sw10 Mto mrefu zaidi duniani ni upi? (expected Nile): Mto mrefu zaidi duniani ni Amazonas [6].
- **Router (both checks)**, sw10 Mto mrefu zaidi duniani ni upi? (expected Nile): Mto mrefu zaidi duniani ni Amazonas [6].
- **Memory only**, sw11 Nani aliandika riwaya ya Kufa Kuzikana? (expected Ken Walibora): Mswaki wa Kufa Kuzikana aliandikwa na aliyekuwa na kujifunza taasisi za Ulema na ujenzi wa dini kati ya Arabi na Bantu.
- **Search: English Wikipedia only**, sw11 Nani aliandika riwaya ya Kufa Kuzikana? (expected Ken Walibora): Harper Lee aliandika riwaya ya Kufa Kuzikana [1].
- **Search: own language + English**, sw11 Nani aliandika riwaya ya Kufa Kuzikana? (expected Ken Walibora): Riwaya ya Kufa Kuzikana aliandika na [1].
- **Router (both checks)**, sw11 Nani aliandika riwaya ya Kufa Kuzikana? (expected Ken Walibora): Riwaya ya Kufa Kuzikana aliandika na [1].
- **Memory only**, sw12 Nani aliandika riwaya ya Rosa Mistika? (expected Euphrase Kezilahabi): Riwaya ya Rosa Mistika aliandika ni Kimera.
- **Search: English Wikipedia only**, sw12 Nani aliandika riwaya ya Rosa Mistika? (expected Euphrase Kezilahabi): Nani aliandika riwaya ya Rosa Mistika? [2]

Riwaya ya Rosa Mistika aliandika kwenye kutoka kwa Steven Saylor [1].
- **Memory only**, sw13 Nani aliandika riwaya ya Siku Njema? (expected Ken Walibora): Sitihe Ali Abdu aliandika riwaya ya Siku Njema.
- **Memory only**, sw14 Shaaban Robert alizaliwa mwaka gani? (expected 1909): Shaaban Robert alizaliwa katika mwaka 1962.
- **Search: English Wikipedia only**, sw14 Shaaban Robert alizaliwa mwaka gani? (expected 1909): Shaaban Robert alizaliwa mwaka 1962 [2].
- **Search: own language + English**, sw14 Shaaban Robert alizaliwa mwaka gani? (expected 1909): Shaaban Robert alizaliwa tarehe 22 Juni 1962 [4].
- **Router (both checks)**, sw14 Shaaban Robert alizaliwa mwaka gani? (expected 1909): Shaaban Robert alizaliwa tarehe 22 Juni 1962 [4].
- **Memory only**, sw15 Nani aliandika riwaya ya Utengano? (expected Said Ahmed Mohamed): Mwanaidi aliandika riwaya ya Utengano.
- **Search: English Wikipedia only**, sw15 Nani aliandika riwaya ya Utengano? (expected Said Ahmed Mohamed): F. Scott Fitzgerald aliandika riwaya ya Utengano [2].
- **Memory only**, sw16 Nani aliandika riwaya ya Kiu? (expected Mohammed Suleiman Mohammed): Aliandikia riwaya ya Kiu ni John Steinbeck.
- **Search: English Wikipedia only**, sw16 Nani aliandika riwaya ya Kiu? (expected Mohammed Suleiman Mohammed): Nani aliandika riwaya ya Kiu? [4] John of Patmos (also called John the Revelator, John the Divine, John the Theologian) aliandika riwaya ya Kiu.
- **Memory only**, sw17 Mji wa Kale wa Lamu uliorodheshwa kuwa Urithi wa Dunia wa UNESCO mwaka gani? (expected 2001): Mji wa Kale wa Lamu uliorodheshwa kuwa Urithi wa Dunia wa UNESCO baada ya miaka 2011.
- **Memory only**, sw18 Mji Mkongwe wa Zanzibar uliorodheshwa kuwa Urithi wa Dunia wa UNESCO mwaka gani? (expected 2000): Mji mkongwe wa Zanzibar uliorodheshwa kuwa Urithi wa Dunia wa UNESCO baada ya 1992.
- **Memory only**, sw19 Nani aliandika riwaya ya Dunia Uwanja wa Fujo? (expected Euphrase Kezilahabi): Mwanzo wa Dunia Uwanja wa Fujo aliandika riwaya ya jirani.
- **Search: English Wikipedia only**, sw19 Nani aliandika riwaya ya Dunia Uwanja wa Fujo? (expected Euphrase Kezilahabi): Max Brooks aliandika riwaya ya dunia uwanja wa fujo katika "World War Z: An Oral History of the Zombie War" [4].
- **Memory only**, sw20 Mlima Kenya una urefu wa mita ngapi? (expected 5199): Mlima Kenya una urefu wa mita 5,895.
- **Memory only**, sw22 Naibu Rais wa sasa wa Kenya ni nani? (expected Kithure Kindiki): Naibu Rais wa sasa wa Kenya ni William Ruto.
- **Memory only**, sw23 Rais wa sasa wa Tanzania ni nani? (expected Samia Suluhu Hassan): Rais wa sasa wa Tanzania ni John Magufuli, lakini kuna changamoto chenye uwezo wa kuelewa kwa ujumla.
- **Memory only**, sw24 Makamu wa Rais wa sasa wa Tanzania ni nani? (expected Deogratius Ndejembi): Rais wa sasa wa Tanzania ni John Magufuli, lakini kuna changamoto chenye uwezo wa kuelewa kwa makamu hili kwa maana ambaye mkono wangu ni kuelewa kwa juhudi.
- **Memory only**, sw25 Waziri Mkuu wa sasa wa Tanzania ni nani? (expected Mwigulu Nchemba): Waziri Mkuu wa sasa wa Tanzania ni Dr. Willy Nyasulu.
- **Memory only**, sw27 Gavana wa sasa wa Benki Kuu ya Kenya ni nani? (expected Kamau Thugge): Gavana wa sasa wa Benki Kuu ya Kenya ni Dr. Patrick Njoroge.
- **Search: own language + English**, sw27 Gavana wa sasa wa Benki Kuu ya Kenya ni nani? (expected Kamau Thugge): Gavana wa sasa wa Benki Kuu ya Kenya ni Daktari Patrick Njoroge [1].
- **Router (both checks)**, sw27 Gavana wa sasa wa Benki Kuu ya Kenya ni nani? (expected Kamau Thugge): Gavana wa sasa wa Benki Kuu ya Kenya ni Daktari Patrick Njoroge [1].
- **Memory only**, sw28 Afisa Mkuu Mtendaji (CEO) wa sasa wa Safaricom ni nani? (expected Peter Ndegwa): Afisa Mkuu Mtendaji wa Safaricom sasa ni Mr. Bob Collymore.
- **Memory only**, sw29 Timu gani ilishinda Ligi Kuu ya Kenya (FKF Premier League) msimu wa 2025/26? (expected Gor Mahia): Ligi Kuu ya Kenya (FKF Premier League) msimu wa 2025/2026 ilishinda kusaidia dhaba wa 2026.
- **Memory only**, sw30 Timu gani ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26? (expected Young Africans): Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26 ilishinda kusanyika kwenye miaka 2025 na 2026.
- **Search: English Wikipedia only**, sw30 Timu gani ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26? (expected Young Africans): Timu gani ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) msimu wa 2025/26? [1]

NBC Sports ilishinda Ligi Kuu ya Tanzania Bara (NBC Premier League) ms
- **Memory only**, sw31 Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? (expected Spain): Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? Uzito Ujamaa Kaskazini Amerika ilishinda.
- **Search: English Wikipedia only**, sw31 Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? (expected Spain): Kombe la Dunia la FIFA mwaka 2026 ilishinda Canada; Mexico; na United States [1].
- **Search: own language + English**, sw31 Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? (expected Spain): Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? Marekani ilishinda Kombe la Dunia la FIFA mwaka 2026 [2].
- **Router (both checks)**, sw31 Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? (expected Spain): Nchi gani ilishinda Kombe la Dunia la FIFA mwaka 2026? Marekani ilishinda Kombe la Dunia la FIFA mwaka 2026 [2].
- **Memory only**, sw32 Rais wa sasa wa Zanzibar ni nani? (expected Hussein Ali Mwinyi): Rais wa sasa wa Zanzibar ni Ali Mohamed Shein.
