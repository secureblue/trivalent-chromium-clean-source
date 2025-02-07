%global numjobs %{_smp_build_ncpus}

Source0: chromium-version.txt

Name:	 trivalent-chromium-clean-source
%{lua:
       local f = io.open(macros['_sourcedir']..'/chromium-version.txt', 'r')
       local content = f:read "*all"
       -- This will dynamically set the version based on chromium's latest stable release channel
       print("Version: "..content.."\n")

       -- This will automatically increment the release every ~32 minutes
       print("Release: "..(os.time() // 2000).."\n")
}
Summary: Chromium's source tarball.
Url:     http://www.chromium.org/Home
License: BSD-3-Clause AND LGPL-2.1-or-later AND Apache-2.0 AND IJG AND MIT AND GPL-2.0-or-later AND ISC AND OpenSSL AND (MPL-1.1 OR GPL-2.0-only OR LGPL-2.0-only)

BuildRequires: git
BuildRequires: python3

%description
Vanilla chromium source, cleaned to reduce size and some proprietary bits.

%build
# obtain depot tools for obtaining source
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH="$(pwd)/depot_tools:$PATH"
mkdir chromium
cd chromium

# obtain source, specific version of source, and needed deps (hooks)
fetch --nohooks --no-history chromium
cd src
git fetch origin refs/tags/%{version}:refs/tags/%{version}
git checkout %{version}
gclient runhooks
gclient sync -D

# codec cleaning (non-exhaustive)
export FFMPEG_TMP_PATH="./third_party/ffmpeg/tmp"
mkdir $FFMPEG_TMP_PATH

rm -r ./third_party/ffmpeg/doc ./third_party/ffmpeg/ffbuild ./third_party/ffmpeg/fftools ./third_party/ffmpeg/libavfilter \
      ./third_party/ffmpeg/libavdevice ./third_party/ffmpeg/libpostproc ./third_party/ffmpeg/libswscale \
      ./third_party/ffmpeg/presets ./third_party/ffmpeg/tests ./third_party/ffmpeg/tools

mv ./third_party/ffmpeg/chromium/config $FFMPEG_TMP_PATH/config
rm ./third_party/ffmpeg/chromium/*
mv $FFMPEG_TMP_PATH/* ./third_party/ffmpeg/chromium/

mv ./third_party/ffmpeg/compat/va_copy.h $FFMPEG_TMP_PATH/va_copy.h
rm ./third_party/ffmpeg/compat/*
mv $FFMPEG_TMP_PATH/* ./third_party/ffmpeg/compat/

rmdir $FFMPEG_TMP_PATH

find ./third_party/openh264/src -type f -not -name '*.h' -delete

# clean
rm -rf ./build/linux/debian_bullseye_amd64-sysroot ./build/linux/debian_bullseye_i386-sysroot ./third_party/node/linux/node-linux-x64 ./third_party/rust-toolchain ./third_party/rust-src

# extra clean
rm -rf ./media/test/data ./third_party/jdk/current ./third_party/liblouis/src/tests/braille-specs \
       ./third_party/blink/web_tests ./third_party/catapult/tracing/test_data ./third_party/depot_tools/.cipd_bin

# compress
cd ..
mv src/ chromium-%{version}/
tar --exclude=\\.git -cf - chromium-%{version} | xz -9 -M 90% -T %{numjobs} -f > chromium-%{version}-clean.tar.xz
mv chromium-%{version}-clean.tar.xz ./../

%install
mkdir -p %{buildroot}%{_usrsrc}/chromium/
install -m 0644 chromium-%{version}-clean.tar.xz %{buildroot}%{_usrsrc}/chromium/

%files
%{_usrsrc}/chromium/chromium-%{version}-clean.tar.xz
