#! /bin/sh -x

wget https://versionhistory.googleapis.com/v1/chrome/platforms/linux/channels/stable/versions/all/releases?filter=endtime=none -O chromium-version.json
grep \"version\" chromium-version.json | grep -oh "[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" > chromium-version.txt

cp ./trivalent-chromium-clean-source/trivalent-chromium-clean-source.spec .
cp ./trivalent-chromium-clean-source/fix-gperf-aarch64.patch .

