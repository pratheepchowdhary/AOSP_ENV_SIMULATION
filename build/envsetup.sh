
# Simulated AOSP envsetup.sh

function gettop
{
    local TOPFILE=build/envsetup.sh
    if [ -n "$TOP" -a -f "$TOP/$TOPFILE" ] ; then
        # The following circumlocution ensures we ensure symlinks get resolved.
        if [ "1" ]; then
            (cd $TOP; pwd -P)
        else
            (cd $TOP; pwd)
        fi
    else
        if [ -f $TOPFILE ] ; then
            # The following circumlocution (repeated below as well) ensures
            # that we check the correct file exists (apart from the same
            # check in the else block) but that the side effect of the cd
            # (here and below) is explicitly localized to within this
            # block, and does not propagate to the caller.
            if [ "1" ]; then
                pwd -P
            else
                pwd
            fi
        else
            local HERE=$PWD
            local T=
            while [ \( ! \( -f $TOPFILE \) \) -a \( $PWD != "/" \) ]; do
                \cd ..
                T=`PWD= /bin/pwd -P`
            done
            \cd $HERE
            if [ -f "$T/$TOPFILE" ]; then
                echo $T
            fi
        fi
    fi
}

function croot()
{
    local T=$(gettop)
    if [ "$T" ]; then
        \cd $(gettop)
    else
        echo "Couldn't locate the top of the tree.  Try setting TOP."
    fi
}

function print_lunch_menu()
{
    echo
    echo "You're building on Linux"
    echo
    echo "Lunch menu... pick a combo:"
    echo "     1. aosp_arm-eng"
    echo "     2. aosp_arm64-eng"
    echo "     3. aosp_x86-eng"
    echo "     4. aosp_x86_64-eng"
    echo "     5. aosp_car_x86_64-userdebug"
    echo "     6. aosp_cf_x86_64_phone-userdebug"
    echo "     7. sdk_phone_x86_64-userdebug"
    echo "     8. my_custom_device-userdebug"
    echo
}

function lunch()
{
    local answer

    if [ "$1" ] ; then
        answer=$1
    else
        print_lunch_menu
        echo -n "Which would you like? [aosp_arm-eng] "
        read answer
    fi

    local selection=

    if [ -z "$answer" ]
    then
        selection=aosp_arm-eng
    elif (echo -n $answer | grep -q -e "^[0-9][0-9]*$")
    then
        if [ $answer -le 8 ] ; then
            # Map numbers to choices
            case $answer in
                1) selection=aosp_arm-eng ;;
                2) selection=aosp_arm64-eng ;;
                3) selection=aosp_x86-eng ;;
                4) selection=aosp_x86_64-eng ;;
                5) selection=aosp_car_x86_64-userdebug ;;
                6) selection=aosp_cf_x86_64_phone-userdebug ;;
                7) selection=sdk_phone_x86_64-userdebug ;;
                8) selection=my_custom_device-userdebug ;;
            esac
        else
            echo "Selection not found."
            return 1
        fi
    else
        selection=$answer
    fi

    export TARGET_PRODUCT=$(echo $selection | sed -e "s/-.*$//")
    export TARGET_BUILD_VARIANT=$(echo $selection | sed -e "s/^.*-//")
    export ANDROID_BUILD_TOP=$(gettop)
    export OUT_DIR=$ANDROID_BUILD_TOP/out
    
    echo
    echo "============================================"
    echo "PLATFORM_VERSION_CODENAME=REL"
    echo "PLATFORM_VERSION=14"
    echo "TARGET_PRODUCT=$TARGET_PRODUCT"
    echo "TARGET_BUILD_VARIANT=$TARGET_BUILD_VARIANT"
    echo "TARGET_BUILD_TYPE=release"
    echo "TARGET_ARCH=arm64"
    echo "TARGET_ARCH_VARIANT=armv8-a"
    echo "HOST_ARCH=x86_64"
    echo "HOST_OS=linux"
    echo "HOST_OS_EXTRA=Linux-x86_64"
    echo "OUT_DIR=$OUT_DIR"
    echo "============================================"
    echo
}

function m()
{
    local T=$(gettop)
    if [ ! "$T" ]; then
        echo "Couldn't locate the top of the tree.  Try setting TOP."
        return
    fi
    
    # Delegate to the python build simulator
    python3 $T/build/fake_build_system.py "$@"
}

function mm()
{
    local T=$(gettop)
    if [ ! "$T" ]; then
        echo "Couldn't locate the top of the tree.  Try setting TOP."
        return
    fi
    
    # Build modules in current directory
    # If arguments are stripped, we pass the current directory to m
    local DIR_TO_BUILD=$PWD
    local REL_DIR=${DIR_TO_BUILD#$T/}
    
    # If we are at top, it's just m
    if [ "$REL_DIR" = "$T" ]; then
        m "$@"
    else
        # We simulate "finding" modules in this dir by passing the dir path as a target/context hint
        # Or in real mm it finds Android.bp in current dir.
        # For this sim, we can just pass the path relative to top.
        echo "Building in $REL_DIR..."
        m "$REL_DIR" "$@"
    fi
}

function mmm()
{
    local T=$(gettop)
    if [ ! "$T" ]; then
        echo "Couldn't locate the top of the tree.  Try setting TOP."
        return
    fi
    
    local DIR=$1
    shift
    
    
    if [ -d "$T/$DIR" ]; then
        echo "Building in $DIR..."
        m "$DIR" "$@"
    else
        echo "Directory $DIR not found."
    fi
}

function mma()
{
  mm "$@"
}

function mmma()
{
  mmm "$@"
}

function refreshmod()
{
    # In real AOSP this updates module-info.json. Here we run m with list-modules which we hooked up to generate it.
    echo "Refreshing module info..."
    m --list-modules >/dev/null
}

function pathmod()
{
    local T=$(gettop)
    if [ ! "$T" ]; then
        echo "Couldn't locate the top of the tree.  Try setting TOP."
        return
    fi
    
    if [ -z "$1" ]; then
        echo "Usage: pathmod <module>"
        return 1
    fi
    
    python3 $T/build/fake_build_system.py --query-path "$1"
}

function gomod()
{
    local path=$(pathmod $@)
    if [ -d "$path" ]; then
        cd "$path"
    else
        if [ -z "$path" ]; then
            echo "Module '$1' not found"
        else
            echo "Path '$path' does not exist"
        fi
        return 1
    fi
}

function outmod()
{
    local T=$(gettop)
    if [ ! "$T" ]; then
        echo "Couldn't locate the top of the tree.  Try setting TOP."
        return
    fi
    
    if [ -z "$1" ]; then
        echo "Usage: outmod <module>"
        return 1
    fi
    
    python3 $T/build/fake_build_system.py --query-out "$1"
}

function allmod()
{
    local T=$(gettop)
    if [ ! "$T" ]; then
        echo "Couldn't locate the top of the tree.  Try setting TOP."
        return
    fi
    
    python3 $T/build/fake_build_system.py --query-all
}

function dirmods()
{
    local T=$(gettop)
    if [ ! "$T" ]; then
        echo "Couldn't locate the top of the tree.  Try setting TOP."
        return
    fi
    
    if [ -z "$1" ]; then
        echo "Usage: dirmods <directory>"
        return 1
    fi
    
    local d=$1
    if [ ! -d "$d" ]; then
        if [ -d "$T/$d" ]; then
            d="$T/$d"
        else
            echo "Directory $d not found."
            return 1
        fi
    fi
     
    python3 $T/build/fake_build_system.py --query-dir "$d"
}
