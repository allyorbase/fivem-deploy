import os
import argparse
from pathlib import Path, PurePath

generic_male_metadata = '''         <ClipDictionaryName>move_m@generic</ClipDictionaryName>
         <ExpressionSetName>expr_set_ambient_male</ExpressionSetName>
         <Pedtype>CIVMALE</Pedtype>
         <MovementClipSet>move_m@business@c</MovementClipSet>
         <StrafeClipSet>move_ped_strafing</StrafeClipSet>
         <MovementToStrafeClipSet>move_ped_to_strafe</MovementToStrafeClipSet>
         <InjuredStrafeClipSet>move_strafe_injured</InjuredStrafeClipSet>
         <FullBodyDamageClipSet>dam_ko</FullBodyDamageClipSet>
         <AdditiveDamageClipSet>dam_ad</AdditiveDamageClipSet>
         <DefaultGestureClipSet>ANIM_GROUP_GESTURE_M_GENERIC</DefaultGestureClipSet>
         <FacialClipsetGroupName>facial_clipset_group_gen_male</FacialClipsetGroupName>
         <DefaultVisemeClipSet>ANIM_GROUP_VISEMES_M_LO</DefaultVisemeClipSet>
         <PoseMatcherName>Male</PoseMatcherName>
         <PoseMatcherProneName>Male_prone</PoseMatcherProneName>
         <GetupSetHash>NMBS_SLOW_GETUPS</GetupSetHash>
         <CreatureMetadataName>ambientPed_upperWrinkles</CreatureMetadataName>
         <DecisionMakerName>DEFAULT</DecisionMakerName>
         <MotionTaskDataSetName>STANDARD_PED</MotionTaskDataSetName>
         <DefaultTaskDataSetName>STANDARD_PED</DefaultTaskDataSetName>
         <PedCapsuleName>STANDARD_MALE</PedCapsuleName>
         <RelationshipGroup>CIVMALE</RelationshipGroup>
         <NavCapabilitiesName>STANDARD_PED</NavCapabilitiesName>
         <PerceptionInfo>DEFAULT_PERCEPTION</PerceptionInfo>
         <DefaultBrawlingStyle>BS_AI</DefaultBrawlingStyle>
         <DefaultUnarmedWeapon>WEAPON_UNARMED</DefaultUnarmedWeapon>
         <Personality>SERVICEMALES</Personality>
         <CombatInfo>DEFAULT</CombatInfo>
         <VfxInfoName>VFXPEDINFO_HUMAN_GENERIC</VfxInfoName>
         <AmbientClipsForFlee>FLEE</AmbientClipsForFlee>
         <AbilityType>SAT_NONE</AbilityType>
         <ThermalBehaviour>TB_WARM</ThermalBehaviour>
         <SuperlodType>SLOD_HUMAN</SuperlodType>
         <ScenarioPopStreamingSlot>SCENARIO_POP_STREAMING_NORMAL</ScenarioPopStreamingSlot>
         <DefaultSpawningPreference>DSP_NORMAL</DefaultSpawningPreference>
         <IsStreamedGfx value="false" />
      </Item>'''

def maybe_extract_file(input_file, out_dir):
    #extract files to desired directory
    # we try and do the operations in /tmp

    tmp = Path('/tmp')
    status = None # exit status for subprocesses

    try:
       suffixes = PurePath(input_file).suffixes
    except err as e:
        print(e)
    
    
    # make tmp directory if not exists
    try: 
        assert(tmp.exists())
        Path(tmp / 'gta_tools').mkdir()
        gta_tools = Path('/tmp/gta_tools')
    except FileExistsError:
        print(' /tmp/gta_tools exists, continuing')
        gta_tools = Path('/tmp/gta_tools')
    except err as e:
        print(e)

    # copy our desired files to the directory first

    status = os.system('cp "{}" "{}"'.format(input_file, gta_tools))
    if status != 0:
        print('Failed to copy files to temporary directory')
        return False

    working_file = gta_tools / input_file.name 
    assert(working_file.exists())


    if '.zip' in suffixes:
        #extract zip
        if os.system('unzip') != 0:
            print('Error locating unzip binary, try running \'sudo apt-get install unzip\' ')
            return False
        
        #now lets try to extract all the files
        status = os.system('unzip "{}" -d "{}"'.format(working_file, working_file.parent / working_file.stem))
        if status != 0:
            print('Error unzipping, returning)')
            return False

    elif '.gz' in suffixes:
        #extract tar
        if os.system('tar --version') != 0:
            print('Error locating tar binary, try running \'sudo apt-get install tar\' ')
            return False

        status = os.system('tar -C "{}" -zxvf "{}"'.format(working_file.parent / working_file.stem, working_file))
        if status != 0:
            print('Error untarring, returning)')
            return False

    elif '.rar' in suffixes:
        #extract tar
        if os.system('unrar') != 0:
            print('Error locating unrar binary, try running \'sudo apt-get install unrar\' ')
            return False
    
        # make output directory
        try:
            Path(working_file.parent / working_file.stem).mkdir()
        except Exception as e:
            print(e)
        status = os.system('cd "{}" && unrar e -y "{}"'.format(working_file.parent / working_file.stem, working_file))
        if status != 0:
            print('Error unrar, returning)')
            return False

    # extract successfull, now copy files to destination
    print("copying")
    try:
        out_dir.mkdir(exist_ok=True)
        print("make dir")
        status = os.system('cp -R "{}" "{}"'.format(working_file.parent / working_file.stem, out_dir))
    except Exception as e:
        print(e)
    print("here is the copy status: {}".format(status))
    if status != 0:
        print('Error copying to destination')
        return False
    
    print("copy success")

    return True


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Tools for FiveM mod management.')
    arg_parser.add_argument('-r','--resources_path', help='Path to server-data/resources directory')
    arg_parser.add_argument('-t', '--mod_type', help='Type of modifications to be process', choices=['maps','peds','scripts'])
    arg_parser.add_argument('-i','--in_dir', help='Path to modification(s) to be installed.')

    args = arg_parser.parse_args()

    if not args.resources_path:
        resources_path_input = input('Please provide your server-data/resources directory:');
    else:
        resources_path_input = args.resources_path
    try:
        resources_path = Path(resources_path_input)
        assert(resources_path.is_dir()) # make sure this is a real directory
    except err as e:
        print(e)


    if not args.mod_type:
        mod_type = input('What kind of modifications are you trying to install? [maps, peds, scripts]');
    else:
        mod_type = args.mod_type
    assert(mod_type in ['maps','peds','scripts']) #make sure

    #check if the directories we want exist, if not make them
    peds_dir = None
    stream_dir = None


    if not args.in_dir:
        in_dir_path = input('What kind of modifications are you trying to install? [maps, peds, scripts]');
    else:
        in_dir_path = args.in_dir
    try:
        in_dir_path = Path(in_dir_path)
        assert(in_dir_path.exists())
    except err as e:
        print(e)

    if mod_type == 'peds':
        peds_dir = resources_path / 'assets'
        stream_dir = peds_dir / 'stream'
        stream_dir.mkdir(parents=True, exist_ok=True)
   
   # print('testing file extract')
   # maybe_extract_file(in_dir_path, resources_path / 'peds')
   # print('done testing file extract and copy')

    #Start with handing our input
    if not in_dir_path.is_dir():
        working_dir = Path('/tmp/gta-tools-rt')
        working_dir.mkdir(exist_ok=True)
        
        maybe_extract_file(in_dir_path, working_dir)
        print(working_dir)

        for f in (working_dir / in_dir_path.stem).iterdir():
            if not f.is_dir():
                try:
                    maybe_extract_file(f, f.parent / f.stem)
                except Exception as e:
                    print(e)
        # overwrite our old in path to our new working directory path
        in_dir_path = working_dir / in_dir_path.stem

    # assume we have a dir of multiple extracted mods, or single mod
    for f in in_dir_path.iterdir():
        print("here is f:{}".format(f))
        if f.is_dir():
            if args.mod_type == 'peds':
                ped_name = None
                #get a name for the ped out of the directory
                for p in f.iterdir():
                    print("here is p:{}".format(p))
                    if p.suffix == '.ymt':
                        ped_name = p.stem
                        break
                if not ped_name:
                    print('Could not find .ymt in directory, skipping...')
                    continue 
                
                ped_name = ped_name.replace('MOD', '')
                ped_name = ped_name.lower()
                ped_name = ped_name.replace(' ', '_')
                
                tmp_ped_dir = stream_dir / ped_name
                try:
                    tmp_ped_dir.mkdir()
                except FileExistsError:
                    print('{} already exists, skipping'.format(tmp_ped_dir))
                except Exception as e:
                    print(e)
                    continue 
                # now rename everything in the temp dir
                for p in f.iterdir():
                    if not p.is_dir():
                        p.rename(f / ped_name / p.suffix)

                #now copy stuff
                try:
                    status = os.system('cp -R "{}/*" "{}"'.format(f, tmp_ped_dir))
                except Exception as e:
                    print(e)
                if status != 0:
                    print('Something went wrong copying the peds directory')

                #edit peds.meta in peds_dir                
                with open(peds_dir / 'peds.meta', 'rw') as fp:
                    #seek to the 3rd line
                    for _ in range(0,3):
                        fp.readline()
                    print("now writing out xml") 
                    fp.write("\t\t<Item>\n")
                    fp.write("\t\t\t<Name>{}</Name>\n".format(ped_name))
                    fp.write(generic_male_metadata)
                    print("wrote, now closing")
                    fp.close()
