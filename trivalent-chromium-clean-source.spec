%global numjobs %{_smp_build_ncpus}

Source0: chromium-version.txt

Name:	 trivalent-chromium-clean-source
%{lua:
  function splitVersionTag(vtag)
    local vtag_array = {}
    local index = 1
    for version_block in string.gmatch(vtag, "%d+") do
      vtag_array[index] = tonumber(version_block)
      index = index + 1
    end
    return vtag_array
  end

  local f = io.open(macros['_sourcedir']..'/chromium-version.txt', 'r')
  local version_tag = f:read "*all"
  f:close()
  -- This IS NOT the version of the browser
  -- It is only used if it is greater than the automated version detection
  -- The point is to update to an arbitrary greater release tag, like early stable or beta tags
  local off_version_tag = "148.0.7778.96"
  -- This was added because Google shipped an update but forgot to ship a security fix:
  --   https://github.com/uazo/cromite/issues/2427
  -- And didn't ship said update in stable.
  -- Instead just pushed the fix the next major version instead.

  local vt = splitVersionTag(version_tag)
  local ovt = splitVersionTag(off_version_tag)

  for i = 1, # vt do
    if vt[i] > ovt[i] then
      break
    elseif ovt[i] > vt[i] then
      version_tag = off_version_tag
      local f = io.open(macros['_sourcedir']..'/chromium-version.txt', 'w')
      f:write(off_version_tag)
      f:close()
      break
    end
  end

  -- This will dynamically set the version based on chromium's latest stable release channel
  print("Version: "..version_tag.."\n")

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
#fetch --nohooks --no-history chromium
cat >.gclient <<EOF
solutions = [
  {
    "name": "src",
    "url": "https://chromium.googlesource.com/chromium/src.git",
    "managed": False,
    "custom_deps": {},
    "custom_vars": {
      "checkout_pgo_profiles": True,
      "checkout_nacl": False,
    }
  },
]
EOF
git clone -b %{version} --depth=2 https://chromium.googlesource.com/chromium/src
gclient sync --no-history

# clean sysroots (we don't need)
rm -rf ./src/build/linux/debian_bullseye_*-sysroot

# extra clean (big stuff that takes up space)
rm -rf ./src/third_party/jdk/current ./src/third_party/catapult/tracing/test_data ./src/third_party/depot_tools/.cipd_bin ./src/buildtools/reclient ./src/third_party/instrumented_libs

# compress
mv src/ chromium-%{version}/
tar --exclude=\\.git -cf - chromium-%{version} | xz -9 -M 90% -T %{numjobs} -f > chromium-%{version}-clean.tar.xz
mv chromium-%{version}-clean.tar.xz ./../

%install
declare -r installDir="%{buildroot}%{_usrsrc}/chromium/"
mkdir -p "${installDir}"
install -m 0644 chromium-%{version}-clean.tar.xz "${installDir}"
install -m 0644 %{SOURCE0} "${installDir}"

%files
%{_usrsrc}/chromium/chromium-%{version}-clean.tar.xz
%{_usrsrc}/chromium/chromium-version.txt
