from collections import defaultdict
import json
import pprint
import os

class Item:
    def __init__(self, ident):
        self.ident = ident
        # you can create objects like this.
        # self.put_object_at_position(Item(ItemManager.ITEM_TYPES[str(item['item'])]['ident']), position)

class Container(Item): # containers are types of objects and can do everything an item can do.
    def __init__(self, ident):
        Item.__init__(self, ident)
        self.base_weight = 1 #TODO: pull this from ItemManager
        self.contained_items = []

    def recalc_weight(self):
        # total weight is the weight of all contained items.
        weight = 0
        for item in self.contained_items:
            weight = weight + item.weight
        weight = weight + self.base_weight # readd the base weight
        pass

    def add_item(self, item):
        self.contained_items.append(item)
        self.recalc_weight()
        pass

    def remove_item(self, item):
        for item_to_check in self.contained_items[:]:
            if item_to_check == item:
                self.contained_items.remove(item_to_check)
                self.recalc_weight()
                return
        pass


class ItemManager:
    def __init__(self):
        self.ITEM_TYPES = defaultdict(dict)
        for root, dirs, files in os.walk('./data/json/items/'):
            for file_data in files:
                if file_data.endswith('.json'):
                    # print(root)
                    # print(dirs)
                    # print(file_data)
                    with open(root+'/'+file_data) as data_file: # load tile config so we know what tile foes with what ident
                        data = json.load(data_file)
                    #unique_keys = []
                    for item in data:
                        try:
                            for key, value in item.items():
                                #print(type(value))
                                if(isinstance(value, list)):
                                    self.ITEM_TYPES[item['ident']][key] = []
                                    for add_value in value:
                                        self.ITEM_TYPES[item['ident']][key].append(str(add_value))
                                else:
                                    self.ITEM_TYPES[item['ident']][key] = str(value)
                                #print('.', end='')
                        except Exception:
                            pass
                            #print('x', end='')

        #print(unique_keys)
        #print()
        print('total ITEM_TYPES loaded: ' + str(len(self.ITEM_TYPES)))


'''
        if qty >= 0 :
            charges = qty
        else:
            if type.tool and type.tool.rand_charges.size() > 1 :
                charge_roll = rng(1, type.tool.rand_charges.size() - 1)
                charges = rng(type.tool.rand_charges[charge_roll - 1], type.tool.rand_charges[charge_roll])
            else:
                charges = type.charges_default()

        if type.gun :
            for mod in type.gun.built_in_mods:
                emplace_back(mod, turn, qty).item_tags.insert("IRREMOVABLE")

            for mod in type.gun.default_mods:
                emplace_back(mod, turn, qty)

        elif type.magazine :
            if type.magazine.count > 0 :
                emplace_back(type.magazine.default_ammo, calendar.turn, type.magazine.count)

        elif type.comestible :
            active = goes_bad() and not rotten()

        elif type.tool :
            if ammo_remaining() and ammo_type() :
                ammo_set(ammo_type().default_ammotype(), ammo_remaining())

        if (type.gun or type.tool) and not magazine_integral() :
            set_var("magazine_converted", True)

        if not type.snippet_category.empty() :
            note = SNIPPET.assign(type.snippet_category)


    def make_corpse(mt, turn, name):
        if not mt.is_valid() :
            debugmsg("tried to make a corpse with an invalid mtype id")

        item result("corpse", turn)
        result.corpse = mt.obj()

        result.active = result.corpse.has_flag(MF_REVIVES)
        if result.active and range(1,21) >= 20 :
            result.item_tags.insert("REVIVE_SPECIAL")

        # This is unconditional because the item constructor above sets result.name to
        # "human corpse".
        result.corpse_name = name

        return result

    def convert(new_type):
        type = find_type(new_type)
        return *self

    def deactivate(*ch, alert):
        if not active :
            return *self; # no-op

        if is_tool() and type.tool.revert_to != "null" :
            if ch and alert and not type.tool.revert_msg.empty() :
                ch.add_msg_if_player(m_info, _(type.tool.revert_msg.c_str()), tname().c_str())

            convert(type.tool.revert_to)
            active = False

        return *self

    def activate(self):
        if active :
            return *self; # no-op

        if type.countdown_interval > 0 :
            item_counter = type.countdown_interval

        active = True

        return *self

    def ammo_set(ammo, qty):
        if qty < 0 :
            # completely fill an integral or existing magazine
            if magazine_integral() or magazine_current() :
                qty = ammo_capacity()

                # else try to add a magazine using default ammo count property if set
            elif magazine_default() != "null" :
                item mag(magazine_default())
                if mag.type.magazine.count > 0 :
                    qty = mag.type.magazine.count
                else:
                    qty = item(magazine_default()).ammo_capacity()




        if qty <= 0 in        ammo_unset()
            return *self


        # handle reloadable tools and guns with no specific ammo type as special case
        if ammo == "null" and not ammo_type() in        if (is_tool() or is_gun()) and magazine_integral() in            curammo = None
                charges = std.min(qty, ammo_capacity())

            return *self


        # check ammo is valid for the item
         itype *atype = item_controller.find_template(ammo)
        if not atype.ammo or not atype.ammo.type.count(ammo_type()) in        debugmsg("Tried to set invalid ammo of %s for %s", atype.nname(qty).c_str(), tname().c_str())
            return *self


        if is_magazine() in        ammo_unset()
            emplace_back(ammo, calendar.turn, std.min(qty, ammo_capacity()))
            if has_flag("NO_UNLOAD") in            contents.back().item_tags.insert("NO_DROP")
                contents.back().item_tags.insert("IRREMOVABLE")


        elif magazine_integral() in        curammo = atype
            charges = std.min(qty, ammo_capacity())

        else:
            if not magazine_current() in             itype *mag = find_type(magazine_default())
                if not mag.magazine in                debugmsg("Tried to set ammo of %s without suitable magazine for %s",
                              atype.nname(qty).c_str(), tname().c_str())
                    return *self


                # if default magazine too small fetch instead closest available match
                if mag.magazine.capacity < qty in                # as above call to magazine_default successful can infer minimum one option exists
                    iter = type.magazines.find(ammo_type())
                    std.vector<itype_id> opts(iter.second.begin(), iter.second.end())
                    std.sort(opts.begin(), opts.end(), [](itype_id lhs, rhs)                    return find_type(lhs).magazine.capacity < find_type(rhs).magazine.capacity
                    })
                    mag = find_type(opts.back())
                    for e in opts)                    if find_type(e).magazine.capacity >= qty in                        mag = find_type(e)
                            break



                emplace_back(mag)

            magazine_current().ammo_set(ammo, qty)


        return *self

    def ammo_unset(self):
        if not is_tool() and not is_gun() and not is_magazine() in        ; # do nothing

        elif is_magazine() in        contents.clear()

        elif magazine_integral() in        curammo = None
            charges = 0

        elif magazine_current() in        magazine_current().ammo_unset()


        return *self

    def set_damage(qty):
        damage_ = std.max(std.min(qty, double(max_damage())), double(min_damage()))
        return *self

    def split(qty):
        if not count_by_charges() or qty <= 0 or qty >= charges in        return item()

        res = *self
        res.charges = qty
        charges -= qty
        return res

    def is_null(self):
        static  std.string s_null("null"); # used alot, need to repeat
        # Actually, should never by null at all.
        return (type == None or type == nullitem() or typeId() == s_null)

    def covers(bp):
        if bp >= num_bp :
            debugmsg("bad body part %d to check in item.covers", static_cast<int>(bp))
            return False

        return get_covered_body_parts().test(bp)

    def get_covered_body_parts(self):
        return get_covered_body_parts(get_side())

    def get_covered_body_parts(s):
        std.bitset<num_bp> res

        if is_gun() in        # Currently only used for guns with the should strap mod, guns might
            # go on another bodypart.
            res.set(bp_torso)


         armor = find_armor_data()
        if armor == None in        return res


        res |= armor.covers

        if not armor.sided in        return res; # Just ignore the side.


        switch(s)    case side.BOTH:
            break

        case side.LEFT:
            res.reset(bp_arm_r)
            res.reset(bp_hand_r)
            res.reset(bp_leg_r)
            res.reset(bp_foot_r)
            break

        case side.RIGHT:
            res.reset(bp_arm_l)
            res.reset(bp_hand_l)
            res.reset(bp_leg_l)
            res.reset(bp_foot_l)
            break


        return res

    def is_sided(self):
        t = find_armor_data()
        return t ? t.sided in False

    def get_side(self):
        # MSVC complains if directly cast double to enum
        return static_cast<side>(static_cast<int>(get_var("lateral", static_cast<int>(side.BOTH))))


    def set_side (side s):
        if not is_sided() :
            return False

        if s == side.BOTH :
            erase_var("lateral")
        else:
            set_var("lateral", static_cast<int>(s))

        return True


    def swap_side(self):
        return set_side(opposite_side(get_side()))


    def is_worn_only_with(it):
        return is_power_armor() and it.is_power_armor() and it.covers(bp_torso)


    def in_its_container(self):
        return in_container(type.default_container)


    def in_container(cont):
        if cont != "null" in        item ret(cont, birthday())
            ret.contents.push_back(*self)
            if made_of(LIQUID) and ret.is_container() in            # Note: we can't use any of the normal container functions as they check the
                # container being suitable (seals, etc.)
                ret.contents.back().charges = charges_per_volume(ret.get_container_capacity())


            ret.invlet = invlet
            return ret
        else:
            return *self



    def charges_per_volume(vol):
        if type.volume == 0 in        return INFINITE_CHARGES; # TODO: items should not have 0 volume at all!

        return count_by_charges() ? vol / type.volume in vol / volume()


    def stacks_with(rhs):
        if type != rhs.type in        return False

        # This function is also used to test whether items counted by charges should be merged, that
        # check the, charges must be ignored. In all other cases (tools/guns), charges are important.
        if not count_by_charges() and charges != rhs.charges in        return False

        if damage_ != rhs.damage_ in        return False

        if burnt != rhs.burnt in        return False

        if active != rhs.active in        return False

        if item_tags != rhs.item_tags in        return False

        if faults != rhs.faults in        return False

        if techniques != rhs.techniques in        return False

        if item_vars != rhs.item_vars in        return False

        if goes_bad() in        # If self goes bad, other item should go bad, too. It only depends on the item type.
            if bday != rhs.bday in            return False

            # Because spoiling items are only processed every processing_speed()-th turn
            # the rotting value becomes slightly different for items that have
            # been created at the same time and place and with the same initial rot.
            if std.abs(rot - rhs.rot) > processing_speed() in            return False
            elif rotten() != rhs.rotten() in            # just to be save that rotten and unrotten food is *never* stacked.
                return False


        if((corpse == None and rhs.corpse != None) or
                (corpse != None and rhs.corpse == None))        return False

        if corpse != None and rhs.corpse != None and corpse.id != rhs.corpse.id in        return False

        if contents.size() != rhs.contents.size() in        return False

        return std.equal(contents.begin(), contents.end(), rhs.contents.begin(), [](item a, b)        return a.charges == b.charges and a.stacks_with(b)
        })


    def merge_charges(rhs):
        if not count_by_charges() or not stacks_with(rhs) in        return False

        # Prevent overflow when either item has "near infinite" charges.
        if charges >= INFINITE_CHARGES / 2 or rhs.charges >= INFINITE_CHARGES / 2 in        charges = INFINITE_CHARGES
            return True

        # We'll just hope that the item counter represents the same thing for both items
        if item_counter > 0 or rhs.item_counter > 0 in        item_counter = (static_cast<double>(item_counter) * charges + static_cast<double>(rhs.item_counter) * rhs.charges) / (charges + rhs.charges)

        charges += rhs.charges
        return True


    def put_in(payload):
        contents.push_back(payload)


    def set_var(name, value):
        std.ostringstream tmpstream
        tmpstream.imbue(std.locale.classic())
        tmpstream << value
        item_vars[name] = tmpstream.str()


    def set_var(name, value):
        std.ostringstream tmpstream
        tmpstream.imbue(std.locale.classic())
        tmpstream << value
        item_vars[name] = tmpstream.str()


    def set_var(name, value):
        item_vars[name] = string_format("%f", value)


    def get_var(name, default_value):
         it = item_vars.find(name)
        if it == item_vars.end() in        return default_value

        return atof(it.second.c_str())


    def set_var(name, value):
        item_vars[name] = value


    def get_var(name, default_value):
         it = item_vars.find(name)
        if it == item_vars.end() in        return default_value

        return it.second


    def get_var(name):
        return get_var(name, "")


    def has_var(name):
        return item_vars.count(name) > 0


    def erase_var(name):
        item_vars.erase(name)


    def clear_vars(self):
        item_vars.clear()


     ivaresc = 001

    def itag2ivar(item_tag, std.map<std.string, item_vars):
        pos = item_tag.find('=')
        if item_tag.at(0) == ivaresc and pos != std.string.npos and pos >= 2 in        std.string var_name, val_decoded
            int svarlen, svarsep
            svarsep = item_tag.find('=')
            svarlen = item_tag.size()
            val_decoded = ""
            var_name = item_tag.substr(1, svarsep - 1); # will assume sanity here for now
            for s = svarsep + 1; s < svarlen; s++) { # cheap and temporary, IFS = [\r\n\t ]
                if item_tag[s] == ivaresc and s < svarlen - 2 in                if item_tag[s + 1] == '0' and item_tag[s + 2] == 'A' in                    s += 2
                        val_decoded.append(1, '\n')
                    elif item_tag[s + 1] == '0' and item_tag[s + 2] == 'D' in                    s += 2
                        val_decoded.append(1, '\r')
                    elif item_tag[s + 1] == '0' and item_tag[s + 2] == '6' in                    s += 2
                        val_decoded.append(1, '\t')
                    elif item_tag[s + 1] == '2' and item_tag[s + 2] == '0' in                    s += 2
                        val_decoded.append(1, ' ')
                    else:
                        val_decoded.append(1, item_tag[s]); # hhrrrmmmmm should be passing \a?

                else:
                    val_decoded.append(1, item_tag[s])


            item_vars[var_name]=val_decoded
            return True
        else:
            return False



    def info(showtext):
        std.vector<iteminfo> dummy
        return info(showtext, dummy)


    def info(showtext, iteminfo):    return info(showtext, iteminfo, 1)


    def info(showtext, info, batch):
        std.stringstream temp1, temp2
        space = "  "
         debug = g != None and (debug_mode or
                                             g.u.has_artifact_with(AEP_SUPER_CLAIRVOYANCE))

        info.clear()

        insert_separation_line = ()        if info.back().sName != "--" in            info.push_back(iteminfo("DESCRIPTION", "--"))



        if not is_null() in        info.push_back(iteminfo("BASE", _("Category: "), "<header>" + get_category().name + "</header>",
                                      -999, True, "", False))
             price_preapoc = price(False) * batch
             price_postapoc = price(True) * batch
            info.push_back(iteminfo("BASE", space + _("Price: "), "<num>",
                                      (double)price_preapoc / 100, False, "$", True, True))
            if price_preapoc != price_postapoc in            info.push_back(iteminfo("BASE", space + _("Barter value: "), "<num>",
                                          (double)price_postapoc / 100, False, "$", True, True))


            converted_volume_scale = 0
             converted_volume = round_up(convert_volume(volume().value(),
                                            converted_volume_scale) * batch, 2)
            info.push_back(iteminfo("BASE", _("<bold>Volume</bold>: "),
                                      string_format("<num> %s", volume_units_abbr()),
                                      converted_volume, converted_volume_scale == 0,
                                      "", False, True))

            info.push_back(iteminfo("BASE", space + _("Weight: "),
                                      string_format("<num> %s", weight_units()),
                                      convert_weight(weight()) * batch, False, "", True, True))

            if not type.rigid in            info.emplace_back("BASE", _("<bold>Rigid</bold>: "), _("No (contents increase volume)"))


            dmg_bash = damage_melee(DT_BASH)
            dmg_cut = damage_melee(DT_CUT)
            dmg_stab = damage_melee(DT_STAB)

            if dmg_bash in            info.emplace_back("BASE", _("Bash: "), "", dmg_bash, True, "", False)

            if dmg_cut in            info.emplace_back("BASE", (dmg_bash ? space in std.string()) + _("Cut: "),
                                   "", dmg_cut, True, "", False)

            if dmg_stab in            info.emplace_back("BASE", ((dmg_bash or dmg_cut) ? space in std.string()) + _("Pierce: "),
                                   "", dmg_stab, True, "", False)


            if dmg_bash or dmg_cut or dmg_stab in            info.push_back(iteminfo("BASE", space + _("To-hit bonus: "),
                                          ((type.m_to_hit > 0) ? "+" in ""),
                                          type.m_to_hit, True, ""))
                info.push_back(iteminfo("BASE", _("Moves per attack: "), "",
                                          attack_time(), True, "", True, True))


            insert_separation_line()

            # Display any minimal stat or skill requirements for the item
            std.vector req
            if type.min_str > 0 in            req.push_back(string_format("%s %d", _("strength"), type.min_str))

            if type.min_dex > 0 in            req.push_back(string_format("%s %d", _("dexterity"), type.min_dex))

            if type.min_int > 0 in            req.push_back(string_format("%s %d", _("intelligence"), type.min_int))

            if type.min_per > 0 in            req.push_back(string_format("%s %d", _("perception"), type.min_per))

            for sk in type.min_skills)            req.push_back(string_format("%s %d", skill_id(sk.first).name().c_str(), sk.second))

            if not req.empty() in            info.emplace_back("BASE", _("<bold>Minimum requirements:</bold>"))
                info.emplace_back("BASE", enumerate_as_string(req))
                insert_separation_line()


             std.vector< material_type*> mat_types = made_of_types()
            if not mat_types.empty() in             material_list = enumerate_as_string(mat_types.begin(), mat_types.end(),
                [](material_type *material)                return string_format("<stat>%s</stat>", _(material.name().c_str()))
                }, False)
                info.push_back(iteminfo("BASE", string_format(_("Material: %s"), material_list.c_str())))

            if has_var("contained_name") in            info.push_back(iteminfo("BASE", string_format(_("Contains: %s"),
                                          get_var("contained_name").c_str())))

            if count_by_charges() and not is_food() in            info.push_back(iteminfo("BASE", _("Amount: "), "<num>", * batch, True, "", True, False, True))

            if debug == True in            if g != NULL in                info.push_back(iteminfo("BASE", _("age: "), "",
                                              to_hours<int>(age()), True, "", True, True))

                     item *food = is_food_container() ? contents.front() in self
                    if food and food.goes_bad() in                    info.push_back(iteminfo("BASE", _("bday rot: "), "",
                                                  to_turns<int>(food.age()), True, "", True, True))
                        info.push_back(iteminfo("BASE", _("temp rot: "), "",
                                                  (int)food.rot, True, "", True, True))
                        info.push_back(iteminfo("BASE", space + _("max rot: "), "",
                                                  food.type.comestible.spoils, True, "", True, True))
                        info.push_back(iteminfo("BASE", space + _("fridge: "), "",
                                                  (int)food.fridge, True, "", True, True))
                        info.push_back(iteminfo("BASE", _("last rot: "), "",
                                                  (int)food.last_rot_check, True, "", True, True))


                info.push_back(iteminfo("BASE", _("burn: "), "",  burnt, True, "", True, True))



         item *food_item = None
        if is_food() in        food_item = self
        elif is_food_container() in        food_item = contents.front()

        if food_item != None in        if g.u.nutrition_for *food_item) != 0 or food_item.type.comestible.quench != 0 in            info.push_back(iteminfo("FOOD", _("<bold>Nutrition</bold>: "), "", g.u.nutrition_for *food_item),
                                          True, "", False, True))
                info.push_back(iteminfo("FOOD", space + _("Quench: "), "", food_item.type.comestible.quench))


            if food_item.type.comestible.fun != 0 in            info.push_back(iteminfo("FOOD", _("Enjoyability: "), "", g.u.fun_for *food_item).first))


            info.push_back(iteminfo("FOOD", _("Portions: "), "", abs(int(food_item.charges) * batch)))
            if(food_item.corpse != NULL and (debug == True or (g != NULL and
                                               (g.u.has_bionic(bionic_id("bio_scent_vision")) or g.u.has_trait(trait_id("CARNIVORE")) or
                                                 g.u.has_artifact_with(AEP_SUPER_CLAIRVOYANCE)))))            info.push_back(iteminfo("FOOD", _("Smells like: ") + food_item.corpse.nname()))


             vits = g.u.vitamins_from(*food_item)
             required_vits = enumerate_as_string(vits.begin(), vits.end(), [](std.pair<vitamin_id, v)            return (g.u.vitamin_rate(v.first) > 0 and v.second != 0) # only display vitamins that we actually require
                       ? string_format("%s (%i%%)", v.first.obj().name().c_str(), int(v.second / (DAYS(1) / float(g.u.vitamin_rate(v.first))) * 100))
                       in std.string()
            })
            if not required_vits.empty() in            info.emplace_back("FOOD", _("Vitamins (RDA): "), required_vits.c_str())


            if food_item.has_flag("CANNIBALISM") in            if not g.u.has_trait_flag("CANNIBAL") in                info.emplace_back("DESCRIPTION", _("* This food contains <bad>human flesh</bad>."))
                else:
                    info.emplace_back("DESCRIPTION", _("* This food contains <good>human flesh</good>."))



            if food_item.is_tainted() in            info.emplace_back("DESCRIPTION", _("* This food is <bad>tainted</bad> and will poison you."))


            #/\EFFECT_SURVIVAL >=3 allows detection of poisonous food
            if food_item.has_flag("HIDDEN_POISON") and g.u.get_skill_level(skill_survival).level() >= 3 in            info.emplace_back("DESCRIPTION", _("* On closer inspection, appears to be <bad>poisonous</bad>."))


            #/\EFFECT_SURVIVAL >=5 allows detection of hallucinogenic food
            if food_item.has_flag("HIDDEN_HALLU") and g.u.get_skill_level(skill_survival).level() >= 5 in            info.emplace_back("DESCRIPTION", _("* On closer inspection, appears to be <neutral>hallucinogenic</neutral>."))


            if food_item.goes_bad() in             rot_time = to_string_clipped(time_duration.from_turns(food_item.type.comestible.spoils))
                info.emplace_back("DESCRIPTION",
                                   string_format(_("* This food is <neutral>perishable</neutral>, takes <info>%s</info> to rot from full freshness, room temperature."),
                                                  rot_time.c_str()))
                if food_item.rotten() in                if g.u.has_bionic(bionic_id("bio_digestion")) in                    info.push_back(iteminfo("DESCRIPTION",
                                                  _("This food has started to <neutral>rot</neutral>, but <info>your bionic digestion can tolerate it</info>.")))
                    elif g.u.has_trait(trait_id("SAPROVORE")) in                    info.push_back(iteminfo("DESCRIPTION",
                                                  _("This food has started to <neutral>rot</neutral>, but <info>you can tolerate it</info>.")))
                    else:
                        info.push_back(iteminfo("DESCRIPTION",
                                                  _("This food has started to <bad>rot</bad>.  <info>Eating</info> it would be a <bad>very bad idea</bad>.")))





        if is_magazine() and not has_flag("NO_RELOAD") in        info.emplace_back("MAGAZINE", _("Capacity: "),
                               string_format(ngettext("<num> round of %s", "<num> rounds of %s", ammo_capacity()),
                                              ammo_type().name().c_str()), ammo_capacity(), True)

            info.emplace_back("MAGAZINE", _("Reload time: "), _("<num> per round"),
                               type.magazine.reload_time, True, "", True, True)

            insert_separation_line()


        if not is_gun() in        if ammo_data() in            if ammo_remaining() > 0 in                info.emplace_back("AMMO", _("Ammunition: "), ammo_data().nname(ammo_remaining()))
                elif is_ammo() in                info.emplace_back("AMMO", _("Types: "),
                                       enumerate_as_string(type.ammo.type.begin(), type.ammo.type.end(),
                    [](ammotype e)                    return e.name()
                    }, False))


                 ammo = *ammo_data().ammo
                if ammo.damage > 0 in                info.emplace_back("AMMO", _("<bold>Damage</bold>: "), "", ammo.damage, True, "", False, False)
                    info.emplace_back("AMMO", space + _("Armor-pierce: "), "", ammo.pierce, True, "", True, False)
                    info.emplace_back("AMMO", _("Range: "), "", ammo.range, True, "", False, False)
                    info.emplace_back("AMMO", space + _("Dispersion: "), "", ammo.dispersion, True, "", True, True)
                    info.emplace_back("AMMO", _("Recoil: "), "", ammo.recoil, True, "", True, True)


                std.vector fx
                if ammo.ammo_effects.count("RECYCLED") in                fx.emplace_back(_("This ammo has been <bad>hand-loaded</bad>"))

                if ammo.ammo_effects.count("NEVER_MISFIRES") in                fx.emplace_back(_("This ammo <good>never misfires</good>"))

                if ammo.ammo_effects.count("INCENDIARY") in                fx.emplace_back(_("This ammo <neutral>starts fires</neutral>"))

                if not fx.empty() in                insert_separation_line()
                    for auto e in fx)                    info.emplace_back("AMMO", e)




        else:
             item *mod = self
             aux = gun_current_mode()
            # if we have an active auxiliary gunmod display stats for self instead
            if aux and aux.is_gunmod() and aux.is_gun() in            mod = *aux
                info.emplace_back("DESCRIPTION", string_format(_("Stats of the active <info>gunmod (%s)</info> are shown."),
                                   mod.tname().c_str()))


            # many statistics are dependent upon loaded ammo
            # if item is unloaded (or is RELOAD_AND_SHOOT) shows approximate stats using default ammo
            item *aprox = None
            item tmp
            if mod.ammo_required() and not mod.ammo_remaining() in            tmp = *mod
                tmp.ammo_set(tmp.ammo_default())
                aprox = tmp


             islot_gun gun = *mod.type.gun
             curammo = mod.ammo_data()

            has_ammo = curammo and mod.ammo_remaining()

            ammo_dam = has_ammo ? curammo.ammo.damage     in 0
            ammo_range = has_ammo ? curammo.ammo.range      in 0
            ammo_pierce = has_ammo ? curammo.ammo.pierce     in 0
            ammo_dispersion = has_ammo ? curammo.ammo.dispersion in 0

             skill = mod.gun_skill().obj()

            info.push_back(iteminfo("GUN", _("Skill used: "), "<info>" + skill.name() + "</info>"))

            if mod.magazine_integral() in            if mod.ammo_capacity() in                info.emplace_back("GUN", _("<bold>Capacity:</bold> "),
                                       string_format(ngettext("<num> round of %s", "<num> rounds of %s", mod.ammo_capacity()),
                                                      mod.ammo_type().name().c_str()), mod.ammo_capacity(), True)

            else:
                info.emplace_back("GUN", _("Type: "), mod.ammo_type().name())
                if mod.magazine_current() in                info.emplace_back("GUN", _("Magazine: "), string_format("<stat>%s</stat>", mod.magazine_current().tname().c_str()))



            if mod.ammo_data() in            info.emplace_back("AMMO", _("Ammunition: "), string_format("<stat>%s</stat>", mod.ammo_data().nname(mod.ammo_remaining()).c_str()))


            if mod.get_gun_ups_drain() in            info.emplace_back("AMMO", string_format(ngettext("Uses <stat>%i</stat> charge of UPS per shot",
                                   "Uses <stat>%i</stat> charges of UPS per shot", mod.get_gun_ups_drain()),
                                   mod.get_gun_ups_drain()))


            insert_separation_line()

            max_gun_range = mod.gun_range(g.u)
            if max_gun_range > 0 in            info.emplace_back("GUN", space + _("Maximum range: "), "<num>", max_gun_range)


            info.emplace_back("GUN", _("Base aim speed: "), "<num>", g.u.aim_per_move(*mod, MAX_RECOIL), True, "", True, True)
            for aim_type type in g.u.get_aim_types(*mod))            # Nameless aim levels don't get an entry.
                if type.name.empty() in                continue

                info.emplace_back("GUN", _(type.name.c_str()))
                max_dispersion = g.u.get_weapon_dispersion(*mod).max()
                range = range_with_even_chance_of_good_hit(max_dispersion + type.threshold)
                info.emplace_back("GUN", _("Even chance of good hit at range: "),
                                   _("<num>"), range)
                aim_mv = g.u.gun_engagement_moves(*mod, type.threshold)
                info.emplace_back("GUN", _("Time to reach aim level: "), _("<num> seconds"),
                                   TICKS_TO_SECONDS(aim_mv), False, "", True, True)


            info.push_back(iteminfo("GUN", _("Damage: "), "", mod.gun_damage(False), True, "", False, False))

            if has_ammo in            temp1.str("")
                temp1 << (ammo_dam >= 0 ? "+" in "")
                # ammo_damage and sum_of_damage don't need to translate.
                info.push_back(iteminfo("GUN", "ammo_damage", "",
                                          ammo_dam, True, temp1.str(), False, False, False))
                info.push_back(iteminfo("GUN", "sum_of_damage", _(" = <num>"),
                                          mod.gun_damage(True), True, "", False, False, False))


            info.push_back(iteminfo("GUN", space + _("Armor-pierce: "), "",
                                      mod.gun_pierce(False), True, "", has_ammo, False))
            if has_ammo in            temp1.str("")
                temp1 << (ammo_pierce >= 0 ? "+" in "")
                # ammo_armor_pierce and sum_of_armor_pierce don't need to translate.
                info.push_back(iteminfo("GUN", "ammo_armor_pierce", "",
                                          ammo_pierce, True, temp1.str(), False, False, False))
                info.push_back(iteminfo("GUN", "sum_of_armor_pierce", _(" = <num>"),
                                          mod.gun_pierce(True), True, "", True, False, False))


            info.push_back(iteminfo("GUN", _("Dispersion: "), "",
                                      mod.gun_dispersion(False), True, "", has_ammo, True))
            if has_ammo in            temp1.str("")
                temp1 << (ammo_range >= 0 ? "+" in "")
                # ammo_dispersion and sum_of_dispersion don't need to translate.
                info.push_back(iteminfo("GUN", "ammo_dispersion", "",
                                          ammo_dispersion, True, temp1.str(), False, True, False))
                info.push_back(iteminfo("GUN", "sum_of_dispersion", _(" = <num>"),
                                          mod.gun_dispersion(True), True, "", True, True, False))


            # if effective sight dispersion differs from actual sight dispersion display both
            act_disp = mod.sight_dispersion()
            eff_disp = g.u.effective_dispersion(act_disp)
            adj_disp = eff_disp - act_disp

            if adj_disp < 0 in            info.emplace_back("GUN", _("Sight dispersion: "),
                                   string_format("%i-%i = <num>", act_disp, -adj_disp), eff_disp, True, "", True, True)
            elif adj_disp > 0 in            info.emplace_back("GUN", _("Sight dispersion: "),
                                   string_format("%i+%i = <num>", act_disp, adj_disp), eff_disp, True, "", True, True)
            else:
                info.emplace_back("GUN", _("Sight dispersion: "), "", eff_disp, True, "", True, True)


            bipod = mod.has_flag("BIPOD")
            if aprox in            if aprox.gun_recoil(g.u) in                info.emplace_back("GUN", _("Approximate recoil: "), "",
                                       aprox.gun_recoil(g.u), True, "", bipod, True)
                    if bipod in                    info.emplace_back("GUN", "bipod_recoil", _(" (with bipod <num>)"),
                                           aprox.gun_recoil(g.u, True), True, "", True, True, False)


            else:
                if mod.gun_recoil(g.u) in                info.emplace_back("GUN", _("Effective recoil: "), "",
                                       mod.gun_recoil(g.u), True, "", bipod, True)
                    if bipod in                    info.emplace_back("GUN", "bipod_recoil", _(" (with bipod <num>)"),
                                           mod.gun_recoil(g.u, True), True, "", True, True, False)




            fire_modes = mod.gun_all_modes()
            if(std.any_of(fire_modes.begin(), fire_modes.end(),
            [](std.pair<std.string, e)        return e.second.qty > 1 and not e.second.melee()
            }))            info.emplace_back("GUN", _("Recommended strength (burst): "), "",
                                   ceil(mod.type.weight / 333.0_gram), True, "", True, True)


            info.emplace_back("GUN", _("Reload time: "),
                               has_flag("RELOAD_ONE") ? _("<num> seconds per round") in _("<num> seconds"),
                               int(gun.reload_time / 16.67), True, "", True, True)

            std.vector fm
            for e in fire_modes)            if e.second.target == self and not e.second.melee() in                fm.emplace_back(string_format("%s (%i)", _(e.second.mode.c_str()), e.second.qty))


            if not fm.empty() in            insert_separation_line()
                info.emplace_back("GUN", _("<bold>Fire modes:</bold> ") + enumerate_as_string(fm))


            if not magazine_integral() in            insert_separation_line()
                 compat = magazine_compatible()
                info.emplace_back("DESCRIPTION", _("<bold>Compatible magazines:</bold> ") +
                enumerate_as_string(compat.begin(), compat.end(), [](itype_id id)                return item_controller.find_template(id).nname(1)
                }))


            if not gun.valid_mod_locations.empty() in            insert_separation_line()

                temp1.str("")
                temp1 << _("<bold>Mods:<bold> ")
                iternum = 0
                for elem in gun.valid_mod_locations)                if iternum != 0 in                    temp1 << "; "

                     free_slots = (elem).second - get_free_mod_locations((elem).first)
                    temp1 << "<bold>" << free_slots << "/" << (elem).second << "</bold> " << elem.first.name()
                    first_mods = True
                    for auto mod in gunmods())                    if(mod.type.gunmod.location == (elem).first) { # if mod for self location
                            if first_mods in                            temp1 << ": "
                                first_mods = False
                            else:
                                temp1 << ", "

                            temp1 << "<stat>" << mod.tname() << "</stat>"


                    iternum++

                temp1 << "."
                info.push_back(iteminfo("DESCRIPTION", temp1.str()))


            if mod.casings_count() in            insert_separation_line()
                tmp = ngettext("Contains <stat>%i</stat> casing",
                                            "Contains <stat>%i</stat> casings", mod.casings_count())
                info.emplace_back("DESCRIPTION", string_format(tmp, mod.casings_count()))



        if is_gunmod() in         auto mod = *type.gunmod

            if is_gun() in            info.push_back(iteminfo("DESCRIPTION",
                                          _("This mod <info>must be attached to a gun</info>, can not be fired separately.")))

            if has_flag("REACH_ATTACK") in            info.push_back(iteminfo("DESCRIPTION",
                                          _("When attached to a gun, <good>allows</good> making <info>reach melee attacks</info> with it.")))

            if mod.dispersion != 0 in            info.push_back(iteminfo("GUNMOD", _("Dispersion modifier: "), "",
                                          mod.dispersion, True, ((mod.dispersion > 0) ? "+" in ""), True, True))

            if mod.sight_dispersion != -1 in            info.push_back(iteminfo("GUNMOD", _("Sight dispersion: "), "",
                                          mod.sight_dispersion, True, "", True, True))

            if mod.aim_speed >= 0 in            info.push_back(iteminfo("GUNMOD", _("Aim speed: "), "",
                                          mod.aim_speed, True, "", True, True))

            if mod.damage != 0 in            info.push_back(iteminfo("GUNMOD", _("Damage: "), "", mod.damage, True,
                                          ((mod.damage > 0) ? "+" in "")))

            if mod.pierce != 0 in            info.push_back(iteminfo("GUNMOD", _("Armor-pierce: "), "", mod.pierce, True,
                                          ((mod.pierce > 0) ? "+" in "")))

            if mod.handling != 0 in            info.emplace_back("GUNMOD", _("Handling modifier: "), mod.handling > 0 ? "+" in "", mod.handling, True)

            if type.mod.ammo_modifier in            info.push_back(iteminfo("GUNMOD",
                                          string_format(_("Ammo: <stat>%s</stat>"), type.mod.ammo_modifier.name().c_str())))


            temp1.str("")
            temp1 << _("Used on: ") << enumerate_as_string(mod.usable.begin(), mod.usable.end(), [](gun_type_type used_on)            return string_format("<info>%s</info>", used_on.name().c_str())
            })

            temp2.str("")
            temp2 << _("Location: ")
            temp2 << mod.location.name()

            info.push_back(iteminfo("GUNMOD", temp1.str()))
            info.push_back(iteminfo("GUNMOD", temp2.str()))


        if is_armor() in        temp1.str("")
            temp1 << _("Covers: ")
            if covers(bp_head) in            temp1 << _("The <info>head</info>. ")

            if covers(bp_eyes) in            temp1 << _("The <info>eyes</info>. ")

            if covers(bp_mouth) in            temp1 << _("The <info>mouth</info>. ")

            if covers(bp_torso) in            temp1 << _("The <info>torso</info>. ")


            if is_sided() and (covers(bp_arm_l) or covers(bp_arm_r)) in            temp1 << _("Either <info>arm</info>. ")
            elif covers(bp_arm_l) and covers(bp_arm_r) in            temp1 << _("The <info>arms</info>. ")
            elif covers(bp_arm_l) in            temp1 << _("The <info>left arm</info>. ")
            elif covers(bp_arm_r) in            temp1 << _("The <info>right arm</info>. ")


            if is_sided() and (covers(bp_hand_l) or covers(bp_hand_r)) in            temp1 << _("Either <info>hand</info>. ")
            elif covers(bp_hand_l) and covers(bp_hand_r) in            temp1 << _("The <info>hands</info>. ")
            elif covers(bp_hand_l) in            temp1 << _("The <info>left hand</info>. ")
            elif covers(bp_hand_r) in            temp1 << _("The <info>right hand</info>. ")


            if is_sided() and (covers(bp_leg_l) or covers(bp_leg_r)) in            temp1 << _("Either <info>leg</info>. ")
            elif covers(bp_leg_l) and covers(bp_leg_r) in            temp1 << _("The <info>legs</info>. ")
            elif covers(bp_leg_l) in            temp1 << _("The <info>left leg</info>. ")
            elif covers(bp_leg_r) in            temp1 << _("The <info>right leg</info>. ")


            if is_sided() and (covers(bp_foot_l) or covers(bp_foot_r)) in            temp1 << _("Either <info>foot</info>. ")
            elif covers(bp_foot_l) and covers(bp_foot_r) in            temp1 << _("The <info>feet</info>. ")
            elif covers(bp_foot_l) in            temp1 << _("The <info>left foot</info>. ")
            elif covers(bp_foot_r) in            temp1 << _("The <info>right foot</info>. ")


            info.push_back(iteminfo("ARMOR", temp1.str()))

            temp1.str("")
            temp1 << _("Layer: ")
            if has_flag("SKINTIGHT") in            temp1 << _("<stat>Close to skin</stat>. ")
            elif has_flag("BELTED") in            temp1 << _("<stat>Strapped</stat>. ")
            elif has_flag("OUTER") in            temp1 << _("<stat>Outer</stat>. ")
            elif has_flag("WAIST") in            temp1 << _("<stat>Waist</stat>. ")
            else:
                temp1 << _("<stat>Normal</stat>. ")


            info.push_back(iteminfo("ARMOR", temp1.str()))

            info.push_back(iteminfo("ARMOR", _("Coverage: "), "<num>%", get_coverage(), True, "", False))
            info.push_back(iteminfo("ARMOR", space + _("Warmth: "), "", get_warmth()))

            insert_separation_line()

            if has_flag("FIT") in            info.push_back(iteminfo("ARMOR", _("<bold>Encumbrance</bold>: "),
                                          _("<num> <info>(fits)</info>"),
                                          get_encumber(), True, "", False, True))
            else:
                info.push_back(iteminfo("ARMOR", _("<bold>Encumbrance</bold>: "), "",
                                          get_encumber(), True, "", False, True))


            converted_storage_scale = 0
             converted_storage = round_up(convert_volume(get_storage().value(),
                                             converted_storage_scale), 2)
            info.push_back(iteminfo("ARMOR", space + _("Storage: "),
                                      string_format("<num> %s", volume_units_abbr()),
                                      converted_storage, converted_storage_scale == 0))

            info.push_back(iteminfo("ARMOR", _("Protection: Bash: "), "", bash_resist(), True, "",
                                      False))
            info.push_back(iteminfo("ARMOR", space + _("Cut: "), "", cut_resist(), True, "", False))
            info.push_back(iteminfo("ARMOR", space + _("Acid: "), "", acid_resist(), True, "", True))
            info.push_back(iteminfo("ARMOR", space + _("Fire: "), "", fire_resist(), True, "", True))
            info.push_back(iteminfo("ARMOR", _("Environmental protection: "), "", get_env_resist()))


        if is_book() :
            insert_separation_line()
             auto book = *type.book
            # Some things about a book you CAN tell by it's cover.
            if not book.skill and not type.can_use("MA_MANUAL"):            info.push_back(iteminfo("BOOK", _("Just for fun.")))

            if type.can_use("MA_MANUAL"):            info.push_back(iteminfo("BOOK", _("Some sort of <info>martial arts training manual</info>.")))

            if book.req == 0 in            info.push_back(iteminfo("BOOK", _("It can be <info>understood by beginners</info>.")))

            if g.u.has_identified(typeId()) in            if book.skill in                if g.u.get_skill_level(book.skill).can_train() in                    info.push_back(iteminfo("BOOK", "",
                                                  string_format(_("Can bring your <info>%s skill to</info> <num>"),
                                                          book.skill.obj().name().c_str()), book.level))


                    if book.req != 0 in                    info.push_back(iteminfo("BOOK", "",
                                                  string_format(_("<info>Requires %s level</info> <num> to understand."),
                                                          book.skill.obj().name().c_str()),
                                                  book.req, True, "", True, True))



                if book.intel != 0 in                info.push_back(iteminfo("BOOK", "",
                                              _("Requires <info>intelligence of</info> <num> to easily read."),
                                              book.intel, True, "", True, True))

                if book.fun != 0 in                info.push_back(iteminfo("BOOK", "",
                                              _("Reading self book affects your morale by <num>"),
                                              book.fun, True, (book.fun > 0 ? "+" in "")))

                info.push_back(iteminfo("BOOK", "",
                                          ngettext("A chapter of self book takes <num> <info>minute to read</info>.",
                                                    "A chapter of self book takes <num> <info>minutes to read</info>.",
                                                    book.time),
                                          book.time, True, "", True, True))
                if book.chapters > 0 in                 unread = get_remaining_chapters(g.u)
                    info.push_back(iteminfo("BOOK", "", ngettext("This book has <num> <info>unread chapter</info>.",
                                              "This book has <num> <info>unread chapters</info>.",
                                              unread),
                                              unread))


                std.vector recipe_list
                for auto  elem in book.recipes)                 knows_it = g.u.knows_recipe(elem.recipe)
                    # If the player knows it, recognize it even if it's not clearly stated.
                    if elem.is_hidden() and not knows_it in                    continue

                    if knows_it in                    # In case the recipe is known, has a different name in the book, the
                        # real name to avoid confusing the player.
                         name = elem.recipe.result_name()
                        recipe_list.push_back("<bold>" + name + "</bold>")
                    else:
                        recipe_list.push_back("<dark>" + elem.name + "</dark>")


                if not recipe_list.empty() in                recipe_line = string_format(
                                                  ngettext("This book contains %1$d crafting recipe: %2$s",
                                                            "This book contains %1$d crafting recipes: %2$s", recipe_list.size()),
                                                  recipe_list.size(), enumerate_as_string(recipe_list).c_str())

                    insert_separation_line()
                    info.push_back(iteminfo("DESCRIPTION", recipe_line))

                if recipe_list.size() != book.recipes.size() in                info.push_back(iteminfo("DESCRIPTION",
                                              _("It might help you figuring out some <good>more recipes</good>.")))

            else:
                info.push_back(iteminfo("BOOK",
                                          _("You need to <info>read self book to see its contents</info>.")))



        if is_container() in         auto c = *type.container

            info.push_back(iteminfo("ARMOR", temp1.str()))

            temp1.str("")
            temp1 << _("This container ")

            if c.seals in            temp1 << _("can be <info>resealed</info>, ")

            if c.watertight in            temp1 << _("is <info>watertight</info>, ")

            if c.preserves in            temp1 << _("<good>preserves spoiling</good>, ")


            temp1 << string_format(_("can store <info>%s %s</info>."),
                                    format_volume(c.contains).c_str(),
                                    volume_units_long())

            info.push_back(iteminfo("CONTAINER", temp1.str()))


        if is_tool() in        if ammo_capacity() != 0 in            info.emplace_back("TOOL", string_format(_("<bold>Charges</bold>: %d"), ammo_remaining()))


            if not magazine_integral() in            if magazine_current() in                info.emplace_back("TOOL", _("Magazine: "), string_format("<stat>%s</stat>", magazine_current().tname().c_str()))


                insert_separation_line()
                 compat = magazine_compatible()
                info.emplace_back("TOOL", _("<bold>Compatible magazines:</bold> "),
                enumerate_as_string(compat.begin(), compat.end(), [](itype_id id)                return item_controller.find_template(id).nname(1)
                }))
            elif ammo_capacity() != 0 in            std.string tmp
                if ammo_type() in                #~ "%s" is ammunition type. This types can't be plural.
                    tmp = ngettext("Maximum <num> charge of %s.", "Maximum <num> charges of %s.", ammo_capacity())
                    tmp = string_format(tmp, ammo_type().name().c_str())
                else:
                    tmp = ngettext("Maximum <num> charge.", "Maximum <num> charges.", ammo_capacity())

                info.emplace_back("TOOL", "", tmp, ammo_capacity())



        if not components.empty() in        info.push_back(iteminfo("DESCRIPTION", string_format(_("Made from: %s"),
                                      _(components_to_string().c_str()))))
        else:
             auto dis = recipe_dictionary.get_uncraft(typeId())
             auto req = dis.disassembly_requirements()
            if not req.is_empty() in             components = req.get_components()
                 components_list = enumerate_as_string(components.begin(), components.end(),
                [](std.vector<item_comp> comps)                return comps.front().to_string()
                })

                insert_separation_line()
                info.push_back(iteminfo("DESCRIPTION",
                                          string_format(_("Disassembling self item takes %s and might yield: %s."),
                                                  to_string_approx(time_duration.from_turns(dis.time / 100)), components_list.c_str())))



        name_quality = [info](std.pair<quality_id, q)        std.string str
            if q.first == quality_jack or q.first == quality_lift in            str = string_format(_("Has level <info>%1$d %2$s</info> quality and is rated at <info>%3$d</info> %4$s"),
                                     q.second, q.first.obj().name.c_str(), (int)convert_weight(q.second * TOOL_LIFT_FACTOR),
                                     weight_units())
            else:
                str = string_format(_("Has level <info>%1$d %2$s</info> quality."),
                                     q.second, q.first.obj().name.c_str())

            info.emplace_back("QUALITIES", "", str)


        for auto q in type.qualities)        name_quality(q)


        if std.any_of(contents.begin(), contents.end(), [](item e in    return not e.type.qualities.empty()
        }))        info.emplace_back("QUALITIES", "", _("Contains items with qualities:"))

        for auto e in contents)        for auto q in e.type.qualities)            name_quality(q)



        if showtext and not is_null() in         std.map<std.string, idescription =
                item_vars.find("description")
            insert_separation_line()
            if not type.snippet_category.empty() in            # Just use the dynamic description
                info.push_back(iteminfo("DESCRIPTION", SNIPPET.get(note)))
            elif idescription != item_vars.end() in            info.push_back(iteminfo("DESCRIPTION", idescription.second))
            else:
                info.push_back(iteminfo("DESCRIPTION", _(type.description.c_str())))

            all_techniques = type.techniques
            all_techniques.insert(techniques.begin(), techniques.end())
            if not all_techniques.empty() in            insert_separation_line()
                info.push_back(iteminfo("DESCRIPTION", _("Techniques: ") +
                enumerate_as_string(all_techniques.begin(), all_techniques.end(), [](matec_id tid)                return string_format("<stat>%s:</stat> <info>%s</info>", tid.obj().name.c_str(), tid.obj().description.c_str())
                })))


            if not is_gunmod() and has_flag("REACH_ATTACK") in            insert_separation_line()
                if has_flag("REACH3") in                info.push_back(iteminfo("DESCRIPTION",
                                              _("* This item can be used to make <stat>long reach attacks</stat>.")))
                else:
                    info.push_back(iteminfo("DESCRIPTION",
                                              _("* This item can be used to make <stat>reach attacks</stat>.")))



            #/\EFFECT_MELEE >2 allows seeing melee damage stats on weapons
            if(debug_mode or (g.u.get_skill_level(skill_melee) > 2 and (damage_melee(DT_BASH) > 0 or
                                damage_melee(DT_CUT) > 0 or damage_melee(DT_STAB) > 0 or type.m_to_hit > 0)))            damage_instance non_crit
                g.u.roll_all_damage(False, non_crit, True, *self)
                damage_instance crit
                g.u.roll_all_damage(True, crit, True, *self)
                attack_cost = g.u.attack_speed(*self)
                insert_separation_line()
                info.push_back(iteminfo("DESCRIPTION", string_format(_("<bold>Average melee damage:</bold>"))))
                info.push_back(iteminfo("DESCRIPTION",
                                          string_format(_("Critical hit chance %d%% - %d%%"),
                                                  int(g.u.crit_chance(0, 100, *self) * 100),
                                                  int(g.u.crit_chance(100, 0, *self) * 100))))
                info.push_back(iteminfo("DESCRIPTION",
                                          string_format(_("%d bashing (%d on a critical hit)"),
                                                  int(non_crit.type_damage(DT_BASH)),
                                                  int(crit.type_damage(DT_BASH)))))
                if non_crit.type_damage(DT_CUT) > 0.0 or crit.type_damage(DT_CUT) > 0.0 in                info.push_back(iteminfo("DESCRIPTION",
                                              string_format(_("%d cutting (%d on a critical hit)"),
                                                      int(non_crit.type_damage(DT_CUT)),
                                                      int(crit.type_damage(DT_CUT)))))

                if non_crit.type_damage(DT_STAB) > 0.0 or crit.type_damage(DT_STAB) > 0.0 in                info.push_back(iteminfo("DESCRIPTION",
                                              string_format(_("%d piercing (%d on a critical hit)"),
                                                      int(non_crit.type_damage(DT_STAB)),
                                                      int(crit.type_damage(DT_STAB)))))

                info.push_back(iteminfo("DESCRIPTION",
                                          string_format(_("%d moves per attack"), attack_cost)))


            #lets display which martial arts styles character can use with self weapon
             auto styles = g.u.ma_styles
             valid_styles = enumerate_as_string(styles.begin(), styles.end(),
            [ self ](matype_id mid)            return mid.obj().has_weapon(typeId()) ? mid.obj().name in std.string()
            })
            if not valid_styles.empty() in            insert_separation_line()
                info.push_back(iteminfo("DESCRIPTION",
                                          std.string(_("You know how to use self with these martial arts styles: ")) +
                                          valid_styles))


            for method in type.use_methods)            insert_separation_line()
                method.second.dump_info(*self, info)


            insert_separation_line()

             auto rep = repaired_with()
            if not rep.empty() in            info.emplace_back("DESCRIPTION", _("<bold>Repaired with</bold>: ") +
                enumerate_as_string(rep.begin(), rep.end(), [](itype_id e)                return item.find_type(e).nname(1)
                }))
                insert_separation_line()

            else:
                info.emplace_back("DESCRIPTION", _("* This item is <bad>not repairable</bad>."))


            if not conductive () in            info.push_back(iteminfo("BASE", string_format(_("* This item <good>does not conduct</good> electricity."))))
            elif has_flag("CONDUCTIVE") in            info.push_back(iteminfo("BASE", string_format(_("* This item effectively <bad>conducts</bad> electricity, it has no guard."))))
            else:
                info.push_back(iteminfo("BASE", string_format(_("* This item <bad>conducts</bad> electricity."))))


            # concatenate base and acquired flags...
            std.vector flags
            std.set_union(type.item_tags.begin(), type.item_tags.end(),
                            item_tags.begin(), item_tags.end(),
                            std.back_inserter(flags))

            # ...and display those which have an info description
            for e in flags)            auto f = json_flag.get(e)
                if not f.info().empty() in                info.emplace_back("DESCRIPTION", string_format("* %s", _(f.info().c_str())))



            if is_armor() in            if has_flag("FIT") in                info.push_back(iteminfo("DESCRIPTION",
                                              _("* This piece of clothing <info>fits</info> you perfectly.")))
                elif has_flag("VARSIZE") in                info.push_back(iteminfo("DESCRIPTION",
                                              _("* This piece of clothing <info>can be refitted</info>.")))

                if is_sided() in                info.push_back(iteminfo("DESCRIPTION",
                                              _("* This item can be worn on <info>either side</info> of the body.")))

                if is_power_armor() in                info.push_back(iteminfo("DESCRIPTION",
                                              _("* This gear is a part of power armor.")))
                    if covers(bp_head) in                    info.push_back(iteminfo("DESCRIPTION",
                                                  _("* When worn with a power armor suit, will <good>fully protect</good> you from <info>radiation</info>.")))
                    else:
                        info.push_back(iteminfo("DESCRIPTION",
                                                  _("* When worn with a power armor helmet, will <good>fully protect</good> you from <info>radiation</info>.")))


                if typeId() == "rad_badge" in                info.push_back(iteminfo("DESCRIPTION",
                                              string_format(_("* The film strip on the badge is %s."),
                                                      rad_badge_color(irridation).c_str())))



            if is_tool() in            if has_flag("USE_UPS") in                info.push_back(iteminfo("DESCRIPTION",
                                              _("* This tool has been modified to use a <info>universal power supply</info> and is <neutral>not compatible</neutral> with <info>standard batteries</info>.")))
                elif has_flag("RECHARGE") and has_flag("NO_RELOAD") in                info.push_back(iteminfo("DESCRIPTION",
                                              _("* This tool has a <info>rechargeable power cell</info> and is <neutral>not compatible</neutral> with <info>standard batteries</info>.")))
                elif has_flag("RECHARGE") in                info.push_back(iteminfo("DESCRIPTION",
                                              _("* This tool has a <info>rechargeable power cell</info> and can be recharged in any <neutral>UPS-compatible recharging station</neutral>. You could charge it with <info>standard batteries</info>, unloading it is impossible.")))



            if has_flag("RADIO_ACTIVATION") in            if has_flag("RADIO_MOD") in                info.emplace_back("DESCRIPTION", _("* This item has been modified to listen to <info>radio signals</info>.  It can still be activated manually."))
                else:
                    info.emplace_back("DESCRIPTION", _("* This item can only be activated by a <info>radio signal</info>."))


                std.string signame
                if has_flag("RADIOSIGNAL_1") in                signame = "<color_c_red>red</color> radio signal."
                elif has_flag("RADIOSIGNAL_2") in                signame = "<color_c_blue>blue</color> radio signal."
                elif has_flag("RADIOSIGNAL_3") in                signame = "<color_c_green>green</color> radio signal."


                info.emplace_back("DESCRIPTION", string_format(_("* It will be activated by the %s."), signame.c_str()))

                if has_flag("RADIO_INVOKE_PROC") in                info.emplace_back("DESCRIPTION",_("* Activating self item with a <info>radio signal</info> will <neutral>detonate</neutral> it immediately."))



            # @todo Unhide when enforcing limits
            if is_bionic() and g.u.has_trait(trait_id("DEBUG_CBM_SLOTS")) in            info.push_back(iteminfo("DESCRIPTION", list_occupied_bps(type.bionic.id,
                                          _("This bionic is installed in the following body part(s):"))))


            if is_gun() and has_flag("FIRE_TWOHAND") in            info.push_back(iteminfo("DESCRIPTION",
                                          _("* This weapon needs <info>two free hands</info> to fire.")))


            if is_gunmod() and has_flag("DISABLE_SIGHTS") in            info.push_back(iteminfo("DESCRIPTION",
                                          _("* This mod <bad>obscures sights</bad> of the base weapon.")))


            if has_flag("LEAK_DAM") and has_flag("RADIOACTIVE") and damage() > 0 in            info.push_back(iteminfo("DESCRIPTION",
                                          _("* The casing of self item has <neutral>cracked</neutral>, an <info>ominous green glow</info>.")))


            if has_flag("LEAK_ALWAYS") and has_flag("RADIOACTIVE") in            info.push_back(iteminfo("DESCRIPTION",
                                          _("* This object is <neutral>surrounded</neutral> by a <info>sickly green glow</info>.")))


            if is_brewable() or (not contents.empty() and contents.front().is_brewable()) in             item brewed = not is_brewable() ? contents.front() in *self
                 btime = brewed.brewing_time()
                if btime <= 2_days in                info.push_back(iteminfo("DESCRIPTION",
                                              string_format(ngettext("* Once set in a vat, will ferment in around %d hour.",
                                                      "* Once set in a vat, will ferment in around %d hours.", to_hours<int>(btime)),
                                                      to_hours<int>(btime))))
                else:
                    info.push_back(iteminfo("DESCRIPTION",
                                              string_format(ngettext("* Once set in a vat, will ferment in around %d day.",
                                                      "* Once set in a vat, will ferment in around %d days.", to_days<int>(btime)),
                                                      to_days<int>(btime))))


                for res in brewed.brewing_results())                info.push_back(iteminfo("DESCRIPTION",
                                              string_format(_("* Fermenting self will produce <neutral>%s</neutral>."),
                                                      nname(res, brewed.charges).c_str())))



            for e in faults)            #~ %1$s is the name of a fault and %2$s is the description of the fault
                info.emplace_back("DESCRIPTION", string_format(_("* <bad>Faulty %1$s</bad>.  %2$s"),
                                   e.obj().name().c_str(), e.obj().description().c_str()))


            # does the item fit in any holsters?
            holsters = Item_factory.find([self](itype e)            if not e.can_use("holster") in                return False

                ptr = dynamic_cast< holster_actor *>(e.get_use("holster").get_actor_ptr())
                return ptr.can_holster(*self)
            })

            if not holsters.empty() in            insert_separation_line()
                info.emplace_back("DESCRIPTION", _("<bold>Can be stored in:</bold> ") +
                                   enumerate_as_string(holsters.begin(), holsters.end(),
                [](itype *e)                return e.nname(1)
                }))


            for u in type.use_methods)             tt = dynamic_cast< delayed_transform_iuse *>(u.second.get_actor_ptr())
                if tt == None in                continue

                 time_to_do = tt.time_to_do(*self)
                if time_to_do <= 0 in                info.push_back(iteminfo("DESCRIPTION", _("It's done and <info>can be activated</info>.")))
                else:
                     time = to_string_clipped(time_duration.from_turns(time_to_do))
                    info.push_back(iteminfo("DESCRIPTION", string_format(_("It will be done in %s."),
                                              time.c_str())))



            std.map<std.string, item_note = item_vars.find("item_note")
            std.map<std.string, item_note_type =
                item_vars.find("item_note_type")

            if item_note != item_vars.end() in            insert_separation_line()
                ntext = ""
                if item_note_type != item_vars.end() in                ntext += string_format(_("%1$s on the %2$s is: "),
                                            item_note_type.second.c_str(), tname().c_str())
                else:
                    ntext += _("Note: ")

                info.push_back(iteminfo("DESCRIPTION", ntext + item_note.second))


            # describe contents
            if not contents.empty() in            for auto mod in is_gun() ? gunmods() in toolmods())                if mod.type.gunmod in                    temp1.str("")
                        if mod.is_irremovable() in                        temp1 << _("Integrated mod: ")
                        else:
                            temp1 << _("Mod: ")

                        temp1 << "<bold>" << mod.tname() << "</bold> (" << mod.type.gunmod.location.name() << ")"

                    insert_separation_line()
                    info.emplace_back("DESCRIPTION", temp1.str())
                    info.emplace_back("DESCRIPTION", _(mod.type.description.c_str()))

                if not contents.front().type.mod in                info.emplace_back("DESCRIPTION", _(contents.front().type.description.c_str()))



            # list recipes you could use it in
            itype_id tid
            if(contents.empty()) { # use self item
                tid = typeId()
            else { # use the contained item
                tid = contents.front().typeId()

             auto known_recipes = g.u.get_learned_recipes().of_component(tid)
            if not known_recipes.empty() in            temp1.str("")
                 inventory inv = g.u.crafting_inventory()

                if known_recipes.size() > 24 in                insert_separation_line()
                    info.push_back(iteminfo("DESCRIPTION",
                                              _("You know dozens of things you could craft with it.")))
                elif known_recipes.size() > 12 in                insert_separation_line()
                    info.push_back(iteminfo("DESCRIPTION", _("You could use it to craft various other things.")))
                else:
                     recipes = enumerate_as_string(known_recipes.begin(), known_recipes.end(),
                    [ inv ](recipe *r)                    if r.requirements().can_make_with_inventory(inv) in                        return r.result_name()
                        else:
                            return string_format("<dark>%s</dark>", r.result_name())

                    })
                    if not recipes.empty() in                    insert_separation_line()
                        info.push_back(iteminfo("DESCRIPTION", string_format(_("You could use it to craft: %s"),
                                                  recipes.c_str())))





        if not info.empty() and info.back().sName == "--" in        info.pop_back()


        temp1.str("")
        for elem in info)        if elem.sType == "DESCRIPTION" in            temp1 << "\n"


            if elem.bDrawName in            temp1 << elem.sName

            pos = elem.sFmt.find("<num>")
            sPost = ""
            if pos != std.string.npos in            temp1 << elem.sFmt.substr(0, pos)
                sPost = elem.sFmt.substr(pos + 5)
            else:
                temp1 << elem.sFmt.c_str()

            if elem.sValue != "-999" in            temp1 << elem.sPlus << "<neutral>" << elem.sValue << "</neutral>"

            temp1 << sPost
            temp1 << ((elem.bNewLine) ? "\n" in "")


        return replace_colors(temp1.str())


    def get_free_mod_locations(location):
        if not is_gun() in        return 0

         islot_gun gt = *type.gun
         loc = gt.valid_mod_locations.find(location)
        if loc == gt.valid_mod_locations.end() in        return 0

        result = loc.second
        for elem in contents)         auto mod = elem.type.gunmod
            if mod and mod.location == location in            result--


        return result


    def engine_displacement(self):
        return type.engine ? type.engine.displacement in 0


     std.string item.symbol()
        return type.sym


    def color_in_inventory(self):
        u = g.u; # TODO: make a reference, a  reference
        ret = c_light_gray

        if has_flag("WET"):        ret = c_cyan
        elif has_flag("LITCIG"):        ret = c_red
        elif is_filthy() in        ret = c_brown
        elif has_flag("LEAK_DAM") and has_flag("RADIOACTIVE") and damage() > 0 in        ret = c_light_green
        elif (active and not is_food() and not is_food_container()) { # Active items show up as yellow
            ret = c_yellow
        elif is_food() or is_food_container() in         preserves = type.container and type.container.preserves
             item to_color = is_food() ? *self in contents.front()
            # Default: permafood, drugs
            # Brown: rotten (for non-saprophages) or non-rotten (for saprophages)
            # Dark gray: inedible
            # Red: morale penalty
            # Yellow: will rot soon
            # Cyan: will rot eventually
             rating = u.will_eat(to_color)
            # TODO: More colors
            switch(rating.value())        case EDIBLE:
            case TOO_FULL:
                if preserves in                # Nothing, food won't rot
                elif to_color.is_going_bad() in                ret = c_yellow
                elif to_color.goes_bad() in                ret = c_cyan

                break
            case INEDIBLE:
            case INEDIBLE_MUTATION:
                ret = c_dark_gray
                break
            case ALLERGY:
            case ALLERGY_WEAK:
            case CANNIBALISM:
                ret = c_red
                break
            case ROTTEN:
                ret = c_brown
                break
            case NAUSEA:
                ret = c_pink
                break
            case NO_TOOL:
                break

        elif is_gun() in        # Guns are green if you are carrying ammo for them
            # ltred if you have ammo but no mags
            # Gun with integrated mag counts as both
            amtype = ammo_type()
            # get_ammo finds uncontained ammo, finds ammo in magazines
            has_ammo = not u.get_ammo(amtype).empty() or not u.find_ammo(*self, False, -1).empty()
            has_mag = magazine_integral() or not u.find_ammo(*self, True, -1).empty()
            if has_ammo and has_mag in            ret = c_green
            elif has_ammo or has_mag in            ret = c_light_red

        elif is_ammo() in        # Likewise, is green if you have guns that use it
            # ltred if you have the gun but no mags
            # Gun with integrated mag counts as both
            has_gun = u.has_item_with([self](item i)            return i.is_gun() and type.ammo.type.count(i.ammo_type())
            })
            has_mag = u.has_item_with([self](item i)            return (i.is_gun() and i.magazine_integral() and type.ammo.type.count(i.ammo_type())) or
                       (i.is_magazine() and type.ammo.type.count(i.ammo_type()))
            })
            if has_gun and has_mag in            ret = c_green
            elif has_gun or has_mag in            ret = c_light_red

        elif is_magazine() in        # Magazines are green if you have guns and ammo for them
            # ltred if you have one but not the other
            amtype = ammo_type()
            has_gun = u.has_item_with([self](item  it)            return it.is_gun() and it.magazine_compatible().count(typeId()) > 0
            })
            has_ammo = not u.find_ammo(*self, False, -1).empty()
            if has_gun and has_ammo in            ret = c_green
            elif has_gun or has_ammo in            ret = c_light_red

        elif is_book():        if u.has_identified(typeId()):            auto tmp = *type.book
                if(tmp.skill and # Book can improve skill: blue
                        u.get_skill_level(tmp.skill).can_train() and
                        u.get_skill_level(tmp.skill) >= tmp.req and
                        u.get_skill_level(tmp.skill) < tmp.level)                ret = c_light_blue
                elif(tmp.skill and # Book can't improve skill right now, maybe later: pink
                           u.get_skill_level(tmp.skill).can_train() and
                           u.get_skill_level(tmp.skill) < tmp.level)                ret = c_pink
                elif(not u.studied_all_recipes(*type)) { # Book can't improve skill anymore, has more recipes: yellow
                    ret = c_yellow

            else:
                ret = c_red; # Book hasn't been identified yet: red

        elif is_bionic():        if not u.has_bionic(type.bionic.id) in            ret = u.bionic_installation_issues(type.bionic.id).empty() ? c_green in c_red


        return ret


    def on_wear(p):
        if is_sided() and get_side() == side.BOTH in        # for sided items wear the item on the side which results in least encumbrance
            lhs = 0, rhs = 0

            set_side(side.LEFT)
             left_enc = p.get_encumbrance(*self)
            for i = 0; i < num_bp; i++)            lhs += left_enc[i].encumbrance


            set_side(side.RIGHT)
             right_enc = p.get_encumbrance(*self)
            for i = 0; i < num_bp; i++)            rhs += right_enc[i].encumbrance


            set_side(lhs <= rhs ? side.LEFT in side.RIGHT)


        # TODO: artifacts currently only work with the player character
        if p == g.u and type.artifact in        g.add_artifact_messages(type.artifact.effects_worn)


        p.on_item_wear(*self)


    def on_takeoff(p):
        p.on_item_takeoff(*self)

        if is_sided():        set_side(side.BOTH)



    def on_wield(p, mv):
        # TODO: artifacts currently only work with the player character
        if p == g.u and type.artifact in        g.add_artifact_messages(type.artifact.effects_wielded)


        # weapons with bayonet/bipod or other generic "unhandiness"
        if has_flag("SLOW_WIELD") and not is_gunmod() in        d = 32.0; # arbitrary linear scaling factor
            if is_gun() in            d /= std.max((float)p.get_skill_level(gun_skill()),  1.0)
            elif is_melee() in            d /= std.max((float)p.get_skill_level(melee_skill()), 1.0)


            penalty = get_var("volume", type.volume / units.legacy_volume_factor) * d
            p.moves -= penalty
            mv += penalty


        # firearms with a folding stock or tool/melee without collapse/retract iuse
        if has_flag("NEEDS_UNFOLD") and not is_gunmod() in        penalty = 50; # 200-300 for guns, 50-150 for melee, as fallback
            if is_gun() in            penalty = std.max(0, 300 - p.get_skill_level(gun_skill()) * 10)
            elif is_melee() in            penalty = std.max(0, 150 - p.get_skill_level(melee_skill()) * 10)


            p.moves -= penalty
            mv += penalty


        std.string msg

        if mv > 500 in        msg = _("It takes you an extremely long time to wield your %s.")
        elif mv > 250 in        msg = _("It takes you a very long time to wield your %s.")
        elif mv > 100 in        msg = _("It takes you a long time to wield your %s.")
        elif mv > 50 in        msg = _("It takes you several seconds to wield your %s.")
        else:
            msg = _("You wield your %s.")


        p.add_msg_if_player(msg.c_str(), tname().c_str())


    def on_pickup(p):
        # Fake characters are used to determine pickup weight and volume
        if p.is_fake() in        return


        # TODO: artifacts currently only work with the player character
        if p == g.u and type.artifact in        g.add_artifact_messages(type.artifact.effects_carried)


        if is_bucket_nonempty() in        for it in contents)            g.m.add_item_or_charges(p.pos(), it)


            contents.clear()



    def on_contents_changed(self):
        if is_non_resealable_container() in        convert(type.container.unseals_into)



    def on_damage(double, damage_type):



    def tname(int quantity, with_prefix):
        std.stringstream ret

        # MATERIALS-TODO: put self in json
        std.string damtext

        if (damage() != 0 or (get_option<bool>("ITEM_HEALTH_BAR") and is_armor())) and not is_null() and with_prefix in        if damage() < 0 in            if get_option<bool>("ITEM_HEALTH_BAR") in                damtext = "<color_" + string_from_color(damage_color()) + ">" + damage_symbol() + " </color>"
                elif is_gun() in                damtext = pgettext("damage adjective", "accurized ")
                else:
                    damtext = pgettext("damage adjective", "reinforced ")

            elif typeId() == "corpse" in            if damage() > 0 in                switch(damage())                case 1:
                        damtext = pgettext("damage adjective", "bruised ")
                        break
                    case 2:
                        damtext = pgettext("damage adjective", "damaged ")
                        break
                    case 3:
                        damtext = pgettext("damage adjective", "mangled ")
                        break
                    default:
                        damtext = pgettext("damage adjective", "pulped ")
                        break


            elif get_option<bool>("ITEM_HEALTH_BAR") in            damtext = "<color_" + string_from_color(damage_color()) + ">" + damage_symbol() + " </color>"
            else:
                damtext = string_format("%s ", get_base_material().dmg_adj(damage()).c_str())


        if not faults.empty() in        damtext.insert(0, _("faulty "))


        vehtext = ""
        if is_engine() and engine_displacement() > 0 in        vehtext = string_format(pgettext("vehicle adjective", "%2.1fL "), engine_displacement() / 100.0)

        elif is_wheel() and type.wheel.diameter > 0 in        vehtext = string_format(pgettext("vehicle adjective", "%d\" "), type.wheel.diameter)


        std.string burntext
        if with_prefix and not made_of(LIQUID) in        if volume() >= 1000_ml and burnt * 125_ml >= volume() in            burntext = pgettext("burnt adjective", "badly burnt ")
            elif burnt > 0 in            burntext = pgettext("burnt adjective", "burnt ")



        std.string maintext
        if is_corpse() or typeId() == "blood" or item_vars.find("name") != item_vars.end() in        maintext = type_name(quantity)
        elif is_gun() or is_tool() or is_magazine() in        ret.str("")
            ret << label(quantity)
            for auto mod in is_gun() ? gunmods() in toolmods())            if not type.gun or not type.gun.built_in_mods.count(mod.typeId()) in                ret << "+"


            maintext = ret.str()
        elif(is_armor() and item_tags.count("wooled") + item_tags.count("furred") +
                   item_tags.count("leather_padded") + item_tags.count("kevlar_padded") > 0)        ret.str("")
            ret << label(quantity)
            ret << "+"
            maintext = ret.str()
        elif contents.size() == 1 in        if contents.front().made_of(LIQUID) in            maintext = string_format(pgettext("item name", "%s of %s"), label(quantity).c_str(),
                                          contents.front().tname(quantity, with_prefix).c_str())
            elif contents.front().is_food() in             contents_count = contents.front().charges > 1 ? contents.front().charges in quantity
                maintext = string_format(pgettext("item name", "%s of %s"), label(quantity).c_str(),
                                          contents.front().tname(contents_count, with_prefix).c_str())
            else:
                maintext = string_format(pgettext("item name", "%s with %s"), label(quantity).c_str(),
                                          contents.front().tname(quantity, with_prefix).c_str())

        elif not contents.empty() in        maintext = string_format(pgettext("item name", "%s, full"), label(quantity).c_str())
        else:
            maintext = label(quantity)


        ret.str("")
        if is_food() in        if rotten() in            ret << _(" (rotten)")
            elif is_going_bad() in            ret << _(" (old)")
            elif is_fresh() in            ret << _(" (fresh)")


            if has_flag("HOT") in            ret << _(" (hot)")

            if has_flag("COLD") in            ret << _(" (cold)")



        if has_flag("FIT") in        ret << _(" (fits)")


        if is_filthy() in        ret << _(" (filthy)")


        if is_tool() and has_flag("USE_UPS") in        ret << _(" (UPS)")

        if has_flag("RADIO_MOD") in        ret << _(" (radio:")
            if has_flag("RADIOSIGNAL_1") in            ret << pgettext("The radio mod is associated with the [R]ed button.", "R)")
            elif has_flag("RADIOSIGNAL_2") in            ret << pgettext("The radio mod is associated with the [B]lue button.", "B)")
            elif has_flag("RADIOSIGNAL_3") in            ret << pgettext("The radio mod is associated with the [G]reen button.", "G)")
            else:
                debugmsg("Why is the radio neither red, blue, green?")
                ret << "?)"



        if has_flag("WET") in        ret << _(" (wet)")

        if has_flag("LITCIG") in        ret << _(" (lit)")

        if already_used_by_player(g.u) in        ret << _(" (used)")


        if active and not is_food() and not is_corpse() and (typeId().length() < 3 or typeId().compare(typeId().length() - 3, 3, "_on") != 0) in        # Usually the items whose ids end in "_on" have the "active" or "on" string already contained
            # in their name, food is active while it rots.
            ret << _(" (active)")


         tagtext = ret.str()

        std.string modtext
        if gunmod_find("barrel_small") in        modtext += _("sawn-off ")

        if has_flag("DIAMOND") in        modtext += std.string(_("diamond")) + " "


        ret.str("")
        #~ This is a string to construct the item name as it is displayed. This format string has been added for maximum flexibility. The strings are: %1$s: Damage text (eg. "bruised"). %2$s: burn adjectives (eg. "burnt"). %3$s: tool modifier text (eg. "atomic"). %4$s: vehicle part text (eg. "3.8-Liter"). $5$s: main item text (eg. "apple"). %6s: tags (eg. "(wet) (fits)").
        ret << string_format(_("%1$s%2$s%3$s%4$s%5$s%6$s"), damtext.c_str(), burntext.c_str(),
                              modtext.c_str(), vehtext.c_str(), maintext.c_str(), tagtext.c_str())

        if item_vars.find("item_note") != item_vars.end() in        #~ %s is an item name. This style is used to denote items with notes.
            return string_format(_("*%s*"), ret.str().c_str())
        else:
            return ret.str()



    def display_name(int quantity):
        name = tname(quantity)
        std.string sidetxt
        std.string amt

        switch(get_side())    case side.BOTH:
            break
        case side.LEFT:
            sidetxt = string_format(" (%s)", _("left"))
            break
        case side.RIGHT:
            sidetxt = string_format(" (%s)", _("right"))
            break

        amount = 0
        has_item = is_container() and contents.size() == 1
        has_ammo = is_ammo_container() and not contents.empty()
        contains = has_item or has_ammo
        show_amt = False

        # We should handle infinite charges properly in all cases.
        if contains in        amount = contents.front().charges
        elif is_book() and get_chapters() > 0 in        # a book which has remaining unread chapters
            amount = get_remaining_chapters(g.u)
        elif ammo_capacity() > 0 in        # anything that can be reloaded including tools, magazines, and auxiliary gunmods
            amount = ammo_remaining()
            show_amt = True
        elif count_by_charges() and not has_infinite_charges() in        # A chargeable item
            amount = charges


        if amount or show_amt in        amt = string_format(" (%i)", amount)


        return string_format("%s%s%s", name.c_str(), sidetxt.c_str(), amt.c_str())


    def color(self):
        if is_null() :
            return c_black
        if is_corpse() in        return corpse.color

        return type.color


    def price(practical):
        res = 0

        visit_items([res, practical](item *e)        if e.rotten() in            # @todo Special case things that stay useful when rotten
                return VisitResponse.NEXT


            child = practical ? e.type.price_post in e.type.price
            if e.damage() > 0 in            # maximal damage is 4, reduction is 40% of the value.
                child -= child * static_cast<double>(e.damage()) / 10


            if e.count_by_charges() or e.made_of(LIQUID) in            # price from json data is for default-sized stack
                child *= e.charges / static_cast<double>(e.type.stack_size)

            elif e.magazine_integral() and e.ammo_remaining() and e.ammo_data() in            # items with integral magazines may contain ammunition which can affect the price
                child += item(e.ammo_data(), calendar.turn, e.charges).price(practical)

            elif e.is_tool() and not e.ammo_type() and e.ammo_capacity() in            # if tool has no ammo (eg. spray can) reduce price proportional to remaining charges
                child *= e.ammo_remaining() / double(std.max(e.type.charges_default(), 1))


            res += child
            return VisitResponse.NEXT
        })

        return res


    # MATERIALS-TODO: add a density field to materials.json
    def weight(include_contents):
        if is_null() in        return 0


        # Items that don't drop aren't really there, they're items just for ease of implementation
        if has_flag("NO_DROP") in        return 0


        ret = units.from_gram(get_var("weight", to_gram(type.weight)))
        if has_flag("REDUCED_WEIGHT") in        ret *= 0.75


        if count_by_charges() in        ret *= charges

        elif is_corpse() in        switch(corpse.size)        case MS_TINY:
                ret =   1000_gram
                break
            case MS_SMALL:
                ret =  40750_gram
                break
            case MS_MEDIUM:
                ret =  81500_gram
                break
            case MS_LARGE:
                ret = 120000_gram
                break
            case MS_HUGE:
                ret = 200000_gram
                break

            if made_of(material_id("veggy")) in            ret /= 3

            if corpse.in_species(FISH) or corpse.in_species(BIRD) or corpse.in_species(INSECT) or made_of(material_id("bone")) in            ret /= 8
            elif made_of(material_id("iron")) or made_of(material_id("steel")) or made_of(material_id("stone")) in            ret *= 7


        elif magazine_integral() and not is_magazine() in        if ammo_type() == ammotype("plutonium") in            ret += ammo_remaining() * find_type(ammo_type().default_ammotype()).weight / PLUTONIUM_CHARGES
            elif ammo_data() in            ret += ammo_remaining() * ammo_data().weight



        # if self is an ammo belt add the weight of any implicitly contained linkages
        if is_magazine() and type.magazine.linkage != "NULL" in        item links(type.magazine.linkage, calendar.turn)
            links.charges = ammo_remaining()
            ret += links.weight()


        # reduce weight for sawn-off weapons capped to the apportioned weight of the barrel
        if gunmod_find("barrel_small") in         b = type.gun.barrel_length
             max_barrel_weight = units.from_gram(to_milliliter(b))
             barrel_weight = units.from_gram(b.value() * type.weight.value() / type.volume.value())
            ret -= std.min(max_barrel_weight, barrel_weight)


        if include_contents in        for elem in contents)            ret += elem.weight()



        return ret


    static units.volume corpse_volume(m_size corpse_size)
        switch(corpse_size)    case MS_TINY:
            return    750_ml
        case MS_SMALL:
            return  30000_ml
        case MS_MEDIUM:
            return  62500_ml
        case MS_LARGE:
            return  92500_ml
        case MS_HUGE:
            return 875000_ml

        debugmsg("unknown monster size for corpse")
        return 0


    def base_volume(self):
        if is_null() in        return 0


        if is_corpse() in        return corpse_volume(corpse.size)


        return type.volume


    def volume(integral):
        if is_null() in        return 0


        if is_corpse() in        return corpse_volume(corpse.size)


         local_volume = get_var("volume", -1)
        units.volume ret
        if local_volume >= 0 in        ret = local_volume * units.legacy_volume_factor
        elif integral in        ret = type.integral_volume
        else:
            ret = type.volume


        if count_by_charges() or made_of(LIQUID) in        ret *= charges


        # Non-rigid items add the volume of the content
        if not type.rigid in        for elem in contents)            ret += elem.volume()



        # Some magazines sit (partly) flush with the item so add less extra volume
        if magazine_current() != None in        ret += std.max(magazine_current().volume() - type.magazine_well, units.volume(0))


        if is_gun():        for auto elem in gunmods())            ret += elem.volume(True)


            # @todo implement stock_length property for guns
            if has_flag("COLLAPSIBLE_STOCK"):            # consider only the base size of the gun (without mods)
                tmpvol = get_var("volume", (type.volume - type.gun.barrel_length) / units.legacy_volume_factor)
                if   (tmpvol <=  3) ; # intentional NOP
                elif(tmpvol <=  5) ret -=  250_ml
                elif(tmpvol <=  6) ret -=  500_ml
                elif(tmpvol <=  9) ret -=  750_ml
                elif(tmpvol <= 12) ret -= 1000_ml
                elif(tmpvol <= 15) ret -= 1250_ml
                else                    ret -= 1500_ml


            if gunmod_find("barrel_small") in            ret -= type.gun.barrel_length



        return ret


    def lift_strength(self):
        return weight() / STR_LIFT_FACTOR + (weight().value() % STR_LIFT_FACTOR.value() != 0)


    def attack_time(self):
        ret = 65 + volume() / 62.5_ml + weight() / 60_gram
        return ret


    def damage_melee(dt):
        assert(dt >= DT_NULL and dt < NUM_DT)
        if is_null() in        return 0


        # effectiveness is reduced by 10% per damage level
        res = type.melee[ dt ]
        res -= res * damage() * 0.1

        # apply type specific flags
        switch(dt)    case DT_BASH:
            if has_flag("REDUCED_BASHING") in            res *= 0.5

            break

        case DT_CUT:
        case DT_STAB:
            if has_flag("DIAMOND") in            res *= 1.3

            break

        default:
            break


        # consider any melee gunmods
        if is_gun() in        std.vector<int> opts = { res
            for e in gun_all_modes())            if e.second.target != self and e.second.melee() in                opts.push_back(e.second.target.damage_melee(dt))


            return *std.max_element(opts.begin(), opts.end())



        return std.max(res, 0)


    def base_damage_melee(self):
        # @todo Caching
        damage_instance ret
        for i = DT_NULL + 1; i < NUM_DT; i++)        dt = static_cast<damage_type>(i)
            dam = damage_melee(dt)
            if dam > 0 in            ret.add_damage(dt, dam)



        return ret


    def base_damage_thrown(self):
        # @todo Create a separate cache for individual items (for modifiers like diamond etc.)
        return type.thrown_damage


    def reach_range(p):
        res = 1

        if has_flag("REACH_ATTACK") in        res = has_flag("REACH3") ? 3 in 2


        # for guns consider any attached gunmods
        if is_gun() and not is_gunmod() in        for m in gun_all_modes())            if p.is_npc() and m.second.flags.count("NPC_AVOID") in                continue

                if m.second.melee() in                res = std.max(res, m.second.qty)




        return res




    def unset_flags(self):
        item_tags.clear()


    def has_flag(f):
        ret = False

        if json_flag.get(f).inherit() :
            for e in is_gun() ? gunmods() in toolmods())
            # gunmods fired separately do not contribute to base gun flags
                if not e.is_gun() and e.has_flag(f) :
                    return True

        # other item type flags
        ret = type.item_tags.count(f)
        if ret:
            return ret

        # now check for item specific flags
        ret = item_tags.count(f)
        return ret

    def has_any_flag(flags):
        for flag in flags):
            if has_flag(flag) :
                return True

        return False


    def set_flag(flag):
        item_tags.insert(flag)
        return *self


    def unset_flag(flag):
        item_tags.erase(flag)
        return *self


    def has_property(prop):
        return type.properties.find(prop) != type.properties.end()


    def get_property_string(prop, def):
         it = type.properties.find(prop)
        return it != type.properties.end() ? it.second in def

    def get_property_long(prop, def):
        it = type.properties.find(prop)
        if it != type.properties.end() :
            char *e = None
            r = std.strtol(it.second.c_str(), e, 10)
            if it.second.size() and *e == '\0' :
                return r

            debugmsg("invalid property '%s' for item '%s'", prop.c_str(), tname().c_str())

        return def

    def get_quality(id):
        return_quality = INT_MIN

        if (id == quality_id("BOIL") and not (contents.empty() or (is_tool() and std.all_of(contents)))):
            if not itm.is_ammo() :
                return False

            ammo_types = itm.type.ammo.type
            return ammo_types.find(ammo_type()) != ammo_types.end()


        for quality in type.qualities):
            if quality.first == id :
                return_quality = quality.second


        for itm in contents);
        return_quality = std.max(return_quality, itm.get_quality(id))


        return return_quality


    def has_technique( tech):
        return type.techniques.count(tech) > 0 or techniques.count(tech) > 0


    def add_technique( tech):
        techniques.insert(tech)


    std.vector<item *> item.toolmods()
        std.vector<item *> res
        if is_tool() in        res.reserve(contents.size())
            for auto e in contents)            if e.is_toolmod() in                res.push_back(e)



        return res


    def toolmods():
        std.vector< item *> res
        if is_tool():
            res.reserve(contents.size())
            for e in contents:
                if(e.is_toolmod()):
                    res.push_back(e)
        return res


    def get_techniques(self):
        std.set<matec_id> result = type.techniques
        result.insert(techniques.begin(), techniques.end())
        return result


    def goes_bad(self):
        return is_food() and type.comestible.spoils


    def get_relative_rot(self):
        return goes_bad() ? rot / double(type.comestible.spoils) in 0


    def set_relative_rot(val):
        if goes_bad() in        rot = type.comestible.spoils * val
            # calc_rot uses last_rot_check (when it's not 0) instead of bday.
            # self makes sure the rotting starts from now, from bday.
            last_rot_check = calendar.turn
            fridge = 0
            active = not rotten()



    def spoilage_sort_order(self):
        item *subject
        bottom = std.numeric_limits<int>.max()

        if type.container and contents.size() >= 1 in        if type.container.preserves in            return bottom - 3

            subject = contents.front()
        else:
            subject = self


        if subject.goes_bad() in        return subject.type.comestible.spoils - subject.rot


        if subject.type.comestible in        if subject.type.category.id == "food" in            return bottom - 3
            elif subject.type.category.id == "drugs" in            return bottom - 2
            else:
                return bottom - 1


        return bottom


    def calc_rot(location):
         now = calendar.turn
        if last_rot_check + 10 < now in         since = (last_rot_check == 0 ? to_turn<int>(bday) in last_rot_check)
             until = (fridge > 0 ? fridge in now)
            if since < until in            # rot (outside of fridge) from bday/last_rot_check until fridge/now
                old = rot
                rot += get_rot_since(since, until, location)
                add_msg(m_debug, "r: %s %d,%d %d.%d", typeId().c_str(), since, until, old, rot)

            last_rot_check = now

            if fridge > 0:            # Flat 20%, from time of putting it into fridge up to now
                rot += (now - fridge) * 0.2
                fridge = 0

            # item stays active to let the item counter work
            if item_counter == 0 and rotten() in            active = False




    def get_storage(self):
        t = find_armor_data()
        if t == None :
            return 0

        return t.storage


    def get_env_resist(self):
         t = find_armor_data()
        if t == None in        return 0

        # it_armor.env_resist is unsigned char
        return static_cast<int>(static_cast<unsigned int>(t.env_resist))


    def is_power_armor(self):
         t = find_armor_data()
        if t == None in        return False

        return t.power_armor


    def get_encumber(self):
         t = find_armor_data()
        if t == None in        # handle wearable guns (eg. shoulder strap) as special case
            return is_gun() ? volume() / 750_ml in 0

        # it_armor.encumber is signed char
        encumber = static_cast<int>(t.encumber)

        # Non-rigid items add additional encumbrance proportional to their volume
        if not type.rigid in        for e in contents)            encumber += e.volume() / 250_ml



        # Fit checked before changes, shouldn't reduce penalties from patching.
        if item_tags.count("FIT") and has_flag("VARSIZE") in        encumber = std.max(encumber / 2, encumber - 10)


         thickness = get_thickness()
         coverage = get_coverage()
        if item_tags.count("wooled") in        encumber += 1 + 3 * coverage / 100

        if item_tags.count("furred") in        encumber += 1 + 4 * coverage / 100


        if item_tags.count("leather_padded") in        encumber += ceil(2 * thickness * coverage / 100.0)

        if item_tags.count("kevlar_padded") in        encumber += ceil(2 * thickness * coverage / 100.0)


        return encumber


    def get_layer(self):
        if has_flag("SKINTIGHT") in        return UNDERWEAR
        elif has_flag("WAIST") in        return WAIST_LAYER
        elif has_flag("OUTER") in        return OUTER_LAYER
        elif has_flag("BELTED") in        return BELTED_LAYER

        return REGULAR_LAYER


    def get_coverage(self):
         t = find_armor_data()
        if t == None in        return 0

        # it_armor.coverage is unsigned char
        return static_cast<int>(static_cast<unsigned int>(t.coverage))


    def get_thickness(self):
         t = find_armor_data()
        if t == None in        return 0

        # it_armor.thickness is unsigned char
        return static_cast<int>(static_cast<unsigned int>(t.thickness))


    def get_warmth(self):
        fur_lined = 0
        wool_lined = 0
         t = find_armor_data()
        if t == None in        return 0

        # it_armor.warmth is signed char
        result = static_cast<int>(t.warmth)

        if item_tags.count("furred") > 0 in        fur_lined = 35 * get_coverage() / 100


        if item_tags.count("wooled") > 0 in        wool_lined = 20 * get_coverage() / 100


        return result + fur_lined + wool_lined



    def brewing_time(self):
        return is_brewable() ? type.brewable.time * calendar.season_from_default_ratio() in 0_turns


     std.vector<itype_id> item.brewing_results()
        static  std.vector<itype_id> nulresult{
        return is_brewable() ? type.brewable.results in nulresult


    def can_revive(self):
        if is_corpse() and corpse.has_flag(MF_REVIVES) and damage() < max_damage() in        return True

        return False


    def ready_to_revive(pos):
        if can_revive() == False:        return False

        age_in_hours = to_hours<int>(age())
        age_in_hours -= int((float)burnt / (volume() / 250_ml))
        if damage() > 0 in        age_in_hours /= (damage() + 1)

        rez_factor = 48 - age_in_hours
        if age_in_hours > 6 and (rez_factor <= 0 or one_in(rez_factor)) in        # If we're a special revival zombie, to get up until the player is nearby.
             isReviveSpecial = has_flag("REVIVE_SPECIAL")
            if isReviveSpecial in             distance = rl_dist(pos, g.u.pos())
                if distance > 3:                return False

                if not one_in(distance + 1):                return False



            return True

        return False


    def count_by_charges(self):
        return type.count_by_charges()


    def craft_has_charges(self):
        if count_by_charges():        return True
        elif not ammo_type() in        return True


        return False


    #ifdef _MSC_VER
    # Deal with MSVC compiler bug (#17791, #17958)
    #pragma optimize("", off)
    #endif

    def bash_resist(to_self):
        if is_null() in        return 0


         base_thickness = get_thickness()
        resist = 0
        padding = 0
        eff_thickness = 1

        # Armor gets an additional multiplier.
        if is_armor() in        # base resistance
            # Don't give reinforced items +armor, more resistance to ripping
             dmg = damage()
             eff_damage = to_self ? std.min(dmg, 0) in std.max(dmg, 0)
            eff_thickness = std.max(1, get_thickness() - eff_damage)

        if item_tags.count("leather_padded") > 0 in        padding += base_thickness

        if item_tags.count("kevlar_padded") > 0 in        padding += base_thickness


         std.vector< material_type*> mat_types = made_of_types()
        if not mat_types.empty() in        for (auto mat in mat_types)            resist += mat.bash_resist()

            # Average based on number of materials.
            resist /= mat_types.size()


        return lround((resist * eff_thickness) + padding)


    def cut_resist(to_self):
        if is_null() in        return 0


         base_thickness = get_thickness()
        resist = 0
        padding = 0
        eff_thickness = 1

        # Armor gets an additional multiplier.
        if is_armor() in        # base resistance
            # Don't give reinforced items +armor, more resistance to ripping
             dmg = damage()
             eff_damage = to_self ? std.min(dmg, 0) in std.max(dmg, 0)
            eff_thickness = std.max(1, base_thickness - eff_damage)

        if item_tags.count("leather_padded") > 0 in        padding += base_thickness

        if item_tags.count("kevlar_padded") > 0 in        padding += base_thickness * 2


         std.vector< material_type*> mat_types = made_of_types()
        if not mat_types.empty() in        for auto mat in mat_types)            resist += mat.cut_resist()

            # Average based on number of materials.
            resist /= mat_types.size()


        return lround((resist * eff_thickness) + padding)


    #ifdef _MSC_VER
    #pragma optimize("", on)
    #endif

    def stab_resist(to_self):
        # Better than hardcoding it in multiple places
        return (int)(0.8f * cut_resist(to_self))


    def acid_resist(to_self):
        if to_self in        # Currently no items are damaged by acid
            return INT_MAX


        resist = 0.0
        if is_null() in        return 0.0


         std.vector< material_type*> mat_types = made_of_types()
        if not mat_types.empty() in        # Not sure why cut and bash get an armor thickness bonus but acid doesn't,
            # but such is the way of the code.

            for auto mat in mat_types)            resist += mat.acid_resist()

            # Average based on number of materials.
            resist /= mat_types.size()


         env = get_env_resist()
        if not to_self and env < 10 in        # Low env protection means it doesn't prevent acid seeping in.
            resist *= env / 10.0


        return lround(resist)


    def fire_resist(to_self):
        if to_self in        # Fire damages items in a different way
            return INT_MAX


        resist = 0.0
        if is_null() in        return 0.0


         std.vector< material_type*> mat_types = made_of_types()
        if not mat_types.empty() in        for auto mat in mat_types)            resist += mat.fire_resist()

            # Average based on number of materials.
            resist /= mat_types.size()


         env = get_env_resist()
        if not to_self and env < 10 in        # Iron resists immersion in magma, iron-clad knight won't.
            resist *= env / 10.0


        return lround(resist)


    def chip_resistance(worst):
        res = worst ? INT_MAX in INT_MIN
        for mat in made_of_types())         val = mat.chip_resist()
            res = worst ? std.min(res, val) in std.max(res, val)


        if res == INT_MAX or res == INT_MIN in        return 2


        if res <= 0 in        return 0


        return res


    def min_damage(self):
        return type.damage_min


    def max_damage(self):
        return type.damage_max


    def mod_damage(qty, dt):
        destroy = False

        if count_by_charges() in        charges -= std.min(type.stack_size * qty, double(charges))
            destroy |= charges == 0


        if qty > 0 in        on_damage(qty, dt)


        if not count_by_charges() in        destroy |= damage_ + qty > max_damage()

            damage_ = std.max(std.min(damage_ + qty, double(max_damage())), double(min_damage()))


        return destroy


    def mod_damage(qty):
        return mod_damage(qty, DT_NULL)


    def inc_damage(self):
        return inc_damage(DT_NULL)


    def damage_color(self):
        # @todo unify with getDurabilityColor

        # reinforced, and nearly destroyed items are special case
        if precise_damage() <= min_damage() in        return c_green

        if damage() <= 0 in        return c_light_green

        if damage() == max_damage() in        return c_red


        # assign other colors proportionally
        q = precise_damage() / max_damage()
        if q > 0.66 in        return c_light_red

        if q > 0.33 in        return c_magenta

        return c_yellow


    def damage_symbol(self):
        # reinforced, and nearly destroyed items are special case
        if damage() < 0 in        return _(R"(++)")

        if damage() == 0 in        return _(R"(or)")

        if damage() == max_damage() in        return _(R"(..)")


        # assign other symbols proportionally
        q = precise_damage() / max_damage()
        if q > 0.66 in        return _(R"(\.)")

        if q > 0.33 in        return _(R"(|.)")

        return _(R"(|\)")


     std.set<itype_id> item.repaired_with()
        static std.set<itype_id> no_repair
        return has_flag("NO_REPAIR")  ? no_repair in type.repair


    def mitigate_damage(du):
         res = resistances(*self)
         mitigation = res.get_effective_resist(du)
        du.amount -= mitigation
        du.amount = std.max(0.0, du.amount)


    def damage_resist(dt, to_self):
        switch(dt)    case DT_NULL:
        case NUM_DT:
            return 0
        case DT_TRUE:
        case DT_BIOLOGICAL:
        case DT_ELECTRIC:
        case DT_COLD:
            # Currently hardcoded:
            # Items can never be damaged by those types
            # But they provide 0 protection from them
            return to_self ? INT_MAX in 0
        case DT_BASH:
            return bash_resist(to_self)
        case DT_CUT:
            return cut_resist (to_self)
        case DT_ACID:
            return acid_resist(to_self)
        case DT_STAB:
            return stab_resist(to_self)
        case DT_HEAT:
            return fire_resist(to_self)
        default:
            debugmsg("Invalid damage type: %d", dt)


        return 0


    def is_two_handed(u):
        if has_flag("ALWAYS_TWOHAND") in        return True

        #/\EFFECT_STR determines which weapons can be wielded with one hand
        return ((weight() / 113_gram) > u.str_cur * 4)


     std.vector<material_id> item.made_of()
        if is_corpse() in        return corpse.mat

        return type.materials


    std.vector< material_type*> item.made_of_types()
        std.vector< material_type*> material_types_composed_of
        for (auto mat_id in made_of())        material_types_composed_of.push_back(mat_id.obj())

        return material_types_composed_of


    def made_of_any(mat_idents):
         mats = made_of()
        if mats.empty() in        return False


        return std.any_of(mats.begin(), mats.end(), [mat_idents](material_id e)        return mat_idents.count(e)
        })


    def only_made_of(mat_idents):
         mats = made_of()
        if mats.empty() in        return False


        return std.all_of(mats.begin(), mats.end(), [mat_idents](material_id e)        return mat_idents.count(e)
        })


    def made_of(mat_ident):
         auto materials = made_of()
        return std.find(materials.begin(), materials.end(), mat_ident) != materials.end()


    def made_of(phase):
        if is_null():        return False

        return (type.phase == phase)



    def conductive(self):
        if is_null() in        return False


        if has_flag("CONDUCTIVE") in        return True


        if has_flag("NONCONDUCTIVE") in        return False


        # If any material has electricity resistance equal to or lower than flesh (1) we are conductive.
         mats = made_of_types()
        return std.any_of(mats.begin(), mats.end(), [](material_type *mt)        return mt.elec_resist() <= 1
        })


    def destroyed_at_zero_charges(self):
        return (is_ammo() or is_food())


    def is_gun(self):
        return type.gun.has_value()


    def is_firearm(self):
        static  std.string primitive_flag("PRIMITIVE_RANGED_WEAPON")
        return is_gun() and not has_flag(primitive_flag)


    def is_silent(self):
        return gun_noise().volume < 5


    def is_gunmod(self):
        return type.gunmod.has_value()


    def is_bionic(self):
        return type.bionic.has_value()


    def is_magazine(self):
        return type.magazine.has_value()


    def is_ammo_belt(self):
        return is_magazine() and has_flag("MAG_BELT")


    def is_bandolier(self):
        return type.can_use("bandolier")


    def is_ammo(self):
        return type.ammo.has_value()


    def is_comestible(self):
        return type.comestible.has_value()


    def is_food(self):
        return is_comestible() and (type.comestible.comesttype == "FOOD" or
                                    type.comestible.comesttype == "DRINK")


    def is_medication(self):
        return is_comestible() and type.comestible.comesttype == "MED"


    def is_brewable(self):
        return type.brewable.has_value()


    def is_food_container(self):
        return (contents.size() >= 1 and contents.front().is_food())


    def is_corpse(self):
        return typeId() == "corpse" and corpse != None


     mtype *item.get_mtype()
        return corpse


    def set_mtype(*  m):
        # This is potentially dangerous, e.g. for corpse items, *must* have a valid mtype pointer.
        if m == None in        debugmsg("setting item.corpse of %s to NULL", tname().c_str())
            return

        corpse = m


    def is_ammo_container(self):
        return not is_magazine() and not contents.empty() and contents.front().is_ammo()


    def is_melee(self):
        for idx = DT_NULL + 1; idx != NUM_DT; ++idx)        if is_melee(static_cast<damage_type>(idx)) in            return True


        return False


    def is_melee(dt):
        return damage_melee(dt) > MELEE_STAT


     islot_armor *item.find_armor_data()
        if type.armor in        return *type.armor

        # Currently the only way to make a non-armor item into armor is to install a gun mod.
        # The gunmods are stored in the items contents, are the contents of a container, the
        # tools in a tool belt (a container actually), the ammo in a quiver (container again).
        for auto mod in gunmods())        if mod.type.armor in            return *mod.type.armor


        return None


    def is_armor(self):
        return find_armor_data() != None or has_flag("IS_ARMOR")


    def is_book(self):
        return type.book.has_value()


    def is_container(self):
        return type.container.has_value()


    def is_watertight_container(self):
        return type.container and type.container.watertight and type.container.seals


    def is_non_resealable_container(self):
        return type.container and not type.container.seals and type.container.unseals_into != "null"


    def is_bucket(self):
        # That "preserves" part is a hack:
        # Currently all non-empty cans are effectively sealed at all times
        # Making them buckets would cause weirdness
        return type.container and
               type.container.watertight and
               not type.container.seals and
               type.container.unseals_into == "null"


    def is_bucket_nonempty(self):
        return is_bucket() and not is_container_empty()


    def is_engine(self):
        return type.engine.has_value()


    def is_wheel(self):
        return type.wheel.has_value()


    def is_fuel(self):
        return type.fuel.has_value()


    def is_toolmod(self):
        return not is_gunmod() and type.mod


    def is_faulty(self):
        return is_engine() ? not faults.empty() in False


    def is_irremovable(self):
        return has_flag("IRREMOVABLE")


    def faults_potential(self):
        std.set<fault_id> res
        if type.engine in        res.insert(type.engine.faults.begin(), type.engine.faults.end())

        return res


    def wheel_area(self):
        return is_wheel() ? type.wheel.diameter * type.wheel.width in 0


    def fuel_energy(self):
        return is_fuel() ? type.fuel.energy in 0.0


    def is_container_empty(self):
        return contents.empty()


    def is_container_full(allow_bucket):
        if is_container_empty() in        return False

        return get_remaining_capacity_for_liquid(contents.front(), allow_bucket) == 0


    def can_reload_with(ammo):
        return is_reloadable_helper(ammo, False)


    def is_reloadable_with(ammo):
        return is_reloadable_helper(ammo, True)


    def is_reloadable_helper(ammo, now):
        if not is_reloadable() in        return False
        elif is_watertight_container() in        return (now ? not is_container_full() in True) and
                   (ammo.empty() or is_container_empty() or contents.front().typeId() == ammo)
        elif magazine_integral() in        if not ammo.empty() in            if ammo_data() in                if ammo_current() != ammo in                    return False

                else:
                    at = find_type(ammo)
                    if not at.ammo or not at.ammo.type.count(ammo_type()) in                    return False



            return now ? (ammo_remaining() < ammo_capacity()) in True
        else:
            return ammo.empty() ? True in magazine_compatible().count(ammo)



    def is_salvageable(self):
        if is_null() in        return False

        return not has_flag("NO_SALVAGE")


    def is_funnel_container(bigger_than):
        if not  is_watertight_container() in        return False

        # todo; consider linking funnel to item or -making- it an active item
        if get_container_capacity() <= bigger_than in        return False; # skip contents check, performance

        if (
            contents.empty() or
            contents.front().typeId() == "water" or
            contents.front().typeId() == "water_acid" or
            contents.front().typeId() == "water_acid_weak")        bigger_than = get_container_capacity()
            return True

        return False


    def is_emissive(self):
        return light.luminance > 0 or type.light_emission > 0


    def is_tool(self):
        return type.tool.has_value()


    def is_tool_reversible(self):
        if is_tool() and type.tool.revert_to != "null" in        item revert(type.tool.revert_to)
            npc n
            revert.type.invoke(n, revert, triPoint(-999, -999, -999))
            return revert.is_tool() and typeId() == revert.typeId()

        return False


    def is_artifact(self):
        return type.artifact.has_value()


    def can_contain(it):
        # @todo Volume check
        return can_contain(*it.type)


    def can_contain(tp):
        if not type.container in        # @todo: Tools etc.
            return False


        if tp.phase == LIQUID and not type.container.watertight in        return False


        # @todo Acid in waterskins
        return True


     item item.get_contained()
        if contents.empty() in        static  item null_item
            return null_item

        return contents.front()


    def spill_contents(c):
        if not is_container() or is_container_empty() in        return True


        if c.is_npc() in        return spill_contents(c.pos())


        while(not contents.empty())        on_contents_changed()
            if contents.front().made_of(LIQUID) in            if not g.handle_liquid_from_container(*self, 1) in                return False

            else:
                c.i_add_or_drop(contents.front())
                contents.erase(contents.begin())



        return True


    def spill_contents(pos):
        if not is_container() or is_container_empty() in        return True


        for item it in contents)        g.m.add_item_or_charges(pos, it)


        contents.clear()
        return True


    def get_chapters(self):
        if not type.book in        return 0

        return type.book.chapters


    def get_remaining_chapters(u):
         var = string_format("remaining-chapters-%d", u.getID())
        return get_var(var, get_chapters())


    def mark_chapter_as_read(u):
         remain = std.max(0, get_remaining_chapters(u) - 1)
         var = string_format("remaining-chapters-%d", u.getID())
        set_var(var, remain)


     material_type item.get_random_material()
        return random_entry(made_of(), material_id.NULL_ID()).obj()


     material_type item.get_base_material()
         mats = made_of()
        return mats.empty() ? material_id.NULL_ID().obj() in mats.front().obj()


    bool item.operator<(item other)
         item_category cat_a = get_category()
         item_category cat_b = other.get_category()
        if cat_a != cat_b:        return cat_a < cat_b
        else:
             item *me = is_container() and not contents.empty() ? contents.front() in self
             item *rhs = other.is_container() and not other.contents.empty() ? other.contents.front() in other

            if me.typeId() == rhs.typeId():            return me.charges < rhs.charges
            else:
                n1 = me.type.nname(1)
                n2 = rhs.type.nname(1)
                return std.lexicographical_compare(n1.begin(), n1.end(),
                                                     n2.begin(), n2.end(), sort_case_insensitive_less())




    def gun_skill(self):
        if not is_gun() in        return skill_id.NULL_ID()

        return type.gun.skill_used


    def gun_type(self):
        static skill_id skill_archery("archery")

        if not is_gun() in        return gun_type_type(std.string())

        #@todo move to JSON and remove extraction of self from "GUN" (via skill id)
        #and from "GUNMOD" (via "mod_targets") in lang/extract_json_strings.py
        if gun_skill() == skill_archery in        if ammo_type() == ammotype("bolt") or typeId() == "bullet_crossbow" in            return gun_type_type(translate_marker_context("gun_type_type", "crossbow"))
            else:
                return gun_type_type(translate_marker_context("gun_type_type", "bow"))


        return gun_type_type(gun_skill().str())


    def melee_skill(self):
        if not is_melee() in        return skill_id.NULL_ID()


        if has_flag("UNARMED_WEAPON") in        return skill_unarmed


        hi = 0
        res = skill_id.NULL_ID()

        for idx = DT_NULL + 1; idx != NUM_DT; ++idx)        val = damage_melee(static_cast<damage_type>(idx))
            sk = skill_by_dt (static_cast<damage_type>(idx))
            if val > hi and sk in            hi = val
                res = sk



        return res


    def gun_dispersion(with_ammo):
        if not is_gun() in        return 0

        dispersion_sum = type.gun.dispersion
        for auto mod in gunmods())        dispersion_sum += mod.type.gunmod.dispersion

        dispersion_sum += damage() * 60
        dispersion_sum = std.max(dispersion_sum, 0)
        if with_ammo and ammo_data() in        dispersion_sum += ammo_data().ammo.dispersion

        # Dividing dispersion by 3 temporarally as a gross adjustment,
        # will bake that adjustment into individual gun definitions in the future.
        # Absolute minimum gun dispersion is 45.
        dispersion_sum = std.max(dispersion_sum / 3, 45)
        return dispersion_sum


    def sight_dispersion(self):
        if not is_gun() in        return 0


        res = has_flag("DISABLE_SIGHTS") ? 500 in type.gun.sight_dispersion

        for auto e in gunmods())         auto mod = *e.type.gunmod
            if mod.sight_dispersion < 0 or mod.aim_speed < 0 in            continue; # skip gunmods which don't provide a sight

            res = std.min(res, mod.sight_dispersion)


        return res


    def gun_damage(with_ammo):
        if not is_gun() in        return 0

        ret = type.gun.damage
        if with_ammo and ammo_data() in        ret += ammo_data().ammo.damage

        for auto mod in gunmods())        ret += mod.type.gunmod.damage

        ret -= damage() * 2
        return ret


    def gun_pierce(with_ammo):
        if not is_gun() in        return 0

        ret = type.gun.pierce
        if with_ammo and ammo_data() in        ret += ammo_data().ammo.pierce

        for auto mod in gunmods())        ret += mod.type.gunmod.pierce

        # TODO: item.damage is not used here, it is in item.gun_damage?
        return ret


    def gun_recoil(p, bipod):
        if not is_gun() or (ammo_required() and not ammo_remaining()) in        return 0


        #/\EFFECT_STR improves the handling of heavier weapons
        # we consider only base weight to avoid exploits
        wt = std.min(type.weight, p.str_cur * 333_gram) / 333.0_gram

        handling = type.gun.handling
        for auto mod in gunmods())        if bipod or not mod.has_flag("BIPOD") in            handling += mod.type.gunmod.handling



        # rescale from JSON units which are intentionally specified as integral values
        handling /= 10

        # algorithm is biased so heavier weapons benefit more from improved handling
        handling = pow(wt, 0.8) * pow(handling, 1.2)

        qty = type.gun.recoil
        if ammo_data() in        qty += ammo_data().ammo.recoil


        # handling could be either a bonus or penalty dependent upon installed mods
        if handling > 1.0 in        return qty / handling
        else:
            return qty * (1.0 + std.abs(handling))



    def gun_range(with_ammo):
        if not is_gun() in        return 0

        ret = type.gun.range
        for auto mod in gunmods())        ret += mod.type.gunmod.range

        if with_ammo and ammo_data() in        ret += ammo_data().ammo.range

        return std.min(std.max(0, ret), RANGE_HARD_CAP)


    def gun_range(*p):
        ret = gun_range(True)
        if p == None in        return ret

        if not p.meets_requirements(*self) in        return 0


        # Reduce bow range until player has twice minimm required strength
        if has_flag("STR_DRAW") in        ret += std.max(0.0, (p.get_str() - type.min_str) * 0.5)


        return std.max(0, ret)


    def ammo_remaining(self):
         item *mag = magazine_current()
        if mag in        return mag.ammo_remaining()


        if is_tool() or is_gun() in        # includes auxiliary gunmods
            return charges


        if is_magazine() or is_bandolier() in        res = 0
            for auto e in contents)            res += e.charges

            return res


        return 0


    def ammo_capacity(self):
        res = 0

         item *mag = magazine_current()
        if mag in        return mag.ammo_capacity()


        if is_tool() in        res = type.tool.max_charges
            for auto e in toolmods())            res *= e.type.mod.capacity_multiplier



        if is_gun() in        res = type.gun.clip
            for auto e in gunmods())            res *= e.type.mod.capacity_multiplier



        if is_magazine() in        res = type.magazine.capacity


        if is_bandolier() in        return dynamic_cast< bandolier_actor *>(type.get_use("bandolier").get_actor_ptr()).capacity


        return res


    def ammo_required(self):
        if is_tool() in        return std.max(type.charges_to_use(), 0)


        if is_gun() in        if not ammo_type() in            return 0
            elif has_flag("FIRE_100") in            return 100
            elif has_flag("FIRE_50") in            return 50
            elif has_flag("FIRE_20") in            return 20
            else:
                return 1



        return 0


    def ammo_sufficient(qty):    return ammo_remaining() >= ammo_required() * qty


    def ammo_consume(qty, pos):    if qty < 0 in        debugmsg("Cannot consume negative quantity of ammo for %s", tname().c_str())
            return 0


        item *mag = magazine_current()
        if mag in        res = mag.ammo_consume(qty, pos)
            if res and ammo_remaining() == 0 in            if mag.has_flag("MAG_DESTROY") in                contents.erase(std.remove_if contents.begin(), contents.end(), [mag](item e in                    return mag == e
                    }))
                elif mag.has_flag("MAG_EJECT") in                g.m.add_item(pos, *mag)
                    contents.erase(std.remove_if contents.begin(), contents.end(), [mag](item e in                    return mag == e
                    }))


            return res


        if is_magazine() in        need = qty
            while(contents.size())            e = *contents.rbegin()
                if need >= e.charges in                need -= e.charges
                    contents.pop_back()
                else:
                    e.charges -= need
                    need = 0
                    break


            return qty - need

        elif is_tool() or is_gun() in        qty = std.min(qty, charges)
            charges -= qty
            if charges == 0 in            curammo = None

            return qty


        return 0


     itype * item.ammo_data()
         item *mag = magazine_current()
        if mag in        return mag.ammo_data()


        if is_ammo() in        return type


        if is_magazine() in        return not contents.empty() ? contents.front().ammo_data() in None


        mods = is_gun() ? gunmods() in toolmods()
        for auto e in mods)        if(e.type.mod.ammo_modifier and
                    item_controller.has_template(itype_id(e.type.mod.ammo_modifier.str())))            return item_controller.find_template(itype_id(e.type.mod.ammo_modifier.str()))



        return curammo


    def ammo_current(self):
         ammo = ammo_data()
        return ammo ? ammo.get_id() in "null"


    def ammo_type(conversion):
        if conversion in        mods = is_gun() ? gunmods() in toolmods()
            for auto e in mods)            if e.type.mod.ammo_modifier in                return e.type.mod.ammo_modifier




        if is_gun() in        return type.gun.ammo
        elif is_tool() in        return type.tool.ammo_id
        elif is_magazine() in        return type.magazine.type

        return ammotype.NULL_ID()


    def ammo_default(conversion):
        res = ammo_type(conversion).default_ammotype()
        return not res.empty() ? res in "NULL"


    def ammo_effects(with_ammo):
        if not is_gun() in        return std.set()


        std.set res = type.gun.ammo_effects
        if with_ammo and ammo_data() in        res.insert(ammo_data().ammo.ammo_effects.begin(), ammo_data().ammo.ammo_effects.end())


        for auto mod in gunmods())        res.insert(mod.type.gunmod.ammo_effects.begin(), mod.type.gunmod.ammo_effects.end())


        return res


    def magazine_integral(self):
        # Finds the first mod which changes magazines and returns if it adds a list of them (can just unset instead)
        # If no mod changes them, if there is a magazine set for the base item type
        for auto m in is_gun() ? gunmods() in toolmods())         auto mod_mags = m.type.mod.magazine_adaptor
            if not mod_mags.empty() in            return std.none_of(mod_mags.begin(), mod_mags.end(), [](std.pair<ammotype, e)                return not e.second.empty()
                })



         mags = type.magazines
        return std.none_of(mags.begin(), mags.end(), [](std.pair<ammotype, e)        return not e.second.empty()
        })


    def magazine_default(conversion):
        mag = type.magazine_default.find(ammo_type(conversion))
        return mag != type.magazine_default.end() ? mag.second in "null"


    def magazine_compatible(conversion):
        # mods that define magazine_adaptor may override the items usual magazines
        mods = is_gun() ? gunmods() in toolmods()
        for auto m in mods)        if not m.type.mod.magazine_adaptor.empty() in            mags = m.type.mod.magazine_adaptor.find(ammo_type(conversion))
                return mags != m.type.mod.magazine_adaptor.end() ? mags.second in std.set<itype_id>()



        mags = type.magazines.find(ammo_type(conversion))
        return mags != type.magazines.end() ? mags.second in std.set<itype_id>()


    item * item.magazine_current()
        iter = std.find_if contents.begin(), contents.end(), [](item it in        return it.is_magazine()
        })
        return iter != contents.end() ? *iter in None


     item * item.magazine_current()
        return const_cast<item *>(self).magazine_current()


    std.vector<item *> item.gunmods()
        std.vector<item *> res
        if is_gun() in        res.reserve(contents.size())
            for auto e in contents)            if e.is_gunmod() in                res.push_back(e)



        return res


    std.vector< item *> item.gunmods()
        std.vector< item *> res
        if is_gun() in        res.reserve(contents.size())
            for auto e in contents)            if e.is_gunmod() in                res.push_back(e)



        return res


    item * item.gunmod_find(itype_id mod)
        mods = gunmods()
        it = std.find_if mods.begin(), mods.end(), [mod](item *e in        return e.typeId() == mod
        })
        return it != mods.end() ? *it in None


     item * item.gunmod_find(itype_id mod)
        return const_cast<item *>(self).gunmod_find(mod)


    def is_gunmod_compatible(mod):
        if not mod.is_gunmod() in        debugmsg("Tried checking compatibility of non-gunmod")
            return ret_val<bool>.make_failure()

        static  gun_type_type pistol_gun_type(translate_marker_context("gun_type_type", "pistol"))

        if not is_gun() in        return ret_val<bool>.make_failure(_("isn't a weapon"))

        elif is_gunmod() in        return ret_val<bool>.make_failure(_("is a gunmod and cannot be modded"))

        elif gunmod_find(mod.typeId()) in        return ret_val<bool>.make_failure(_("already has a %s"), mod.tname(1).c_str())

        elif not type.gun.valid_mod_locations.count(mod.type.gunmod.location) in        return ret_val<bool>.make_failure(_("doesn't have a slot for self mod"))

        elif get_free_mod_locations(mod.type.gunmod.location) <= 0 in        return ret_val<bool>.make_failure(_("doesn't have enough room for another %s mod"),
                                                mod.type.gunmod.location.name().c_str())

        elif not mod.type.gunmod.usable.count(gun_type()) in        return ret_val<bool>.make_failure(_("cannot have a %s"), mod.tname().c_str())

        elif typeId() == "hand_crossbow" and not !mod.type.gunmod.usable.count(pistol_gun_type) in        return ret_val<bool>.make_failure(_("isn't big enough to use that mod"))

        elif not mod.type.mod.acceptable_ammo.empty() and not mod.type.mod.acceptable_ammo.count(ammo_type(False)) in        #~ %1$s - name of the gunmod, %2$s - name of the ammo
            return ret_val<bool>.make_failure(_("%1$s cannot be used on %2$s"), mod.tname(1).c_str(),
                                                ammo_type(False).name().c_str())

        elif mod.typeId() == "waterproof_gunmod" and has_flag("WATERPROOF_GUN") in        return ret_val<bool>.make_failure(_("is already waterproof"))

        elif mod.typeId() == "tuned_mechanism" and has_flag("NEVER_JAMS") in        return ret_val<bool>.make_failure(_("is already eminently reliable"))

        elif mod.typeId() == "brass_catcher" and has_flag("RELOAD_EJECT") in        return ret_val<bool>.make_failure(_("cannot have a brass catcher"))

        elif (mod.type.mod.ammo_modifier or not mod.type.mod.magazine_adaptor.empty() :
                   and (ammo_remaining() > 0 or magazine_current()))        return ret_val<bool>.make_failure(_("must be unloaded before installing self mod"))


        return ret_val<bool>.make_success()


    std.map<std.string, item.gun_all_modes()
        std.map<std.string, res

        if not is_gun() or is_gunmod() in        return res


        opts = gunmods()
        opts.push_back(self)

        for auto e in opts)
            # handle base item plus any auxiliary gunmods
            if e.is_gun() in            for auto m in e.type.gun.modes)                # prefix attached gunmods, eg. M203_DEFAULT to avoid index key collisions
                    prefix = e.is_gunmod() ? (std.string(e.typeId()) += "_") in ""
                    std.transform(prefix.begin(), prefix.end(), prefix.begin(), (int(*)(int))std.toupper)

                    qty = std.get<1>(m.second)
                    if m.first == "AUTO" and e == self and has_flag("RAPIDFIRE") in                    qty *= 1.5


                    res.emplace(prefix += m.first, item.gun_mode(std.get<0>(m.second), *>(e),
                                 qty, std.get<2>(m.second)))


                # non-auxiliary gunmods may provide additional modes for the base item
            elif e.is_gunmod() in            for auto m in e.type.gunmod.mode_modifier)                res.emplace(m.first, item.gun_mode { std.get<0>(m.second), *>(e),
                                                           std.get<1>(m.second), std.get<2>(m.second) })




        return res


     item.gun_mode item.gun_get_mode(std.string mode)
        if is_gun() in        for auto e in gun_all_modes())            if e.first == mode in                return e.second



        return gun_mode()


    def gun_current_mode(self):
        return gun_get_mode(const_cast<item *>(self).gun_get_mode_id())


    def gun_get_mode_id(self):
        if not is_gun() or is_gunmod() in        return ""

        return get_var(GUN_MODE_VAR_NAME, "DEFAULT")


    def gun_set_mode(mode):
        if not is_gun() or is_gunmod() or not gun_all_modes().count(mode) in        return False

        set_var(GUN_MODE_VAR_NAME, mode)
        return True


    def gun_cycle_mode(self):
        if not is_gun() or is_gunmod() in        return


        cur = gun_get_mode_id()
        modes = gun_all_modes()

        for iter = modes.begin(); iter != modes.end(); ++iter)        if iter.first == cur in            if std.next(iter) == modes.end() in                break

                gun_set_mode(std.next(iter).first)
                return


        gun_set_mode(modes.begin().first)

        return


     item.gun_mode item.gun_current_mode()
        return const_cast<item *>(self).gun_current_mode()


     use_function *item.get_use(std.string use_name)
        if type != None and type.get_use(use_name) != None in        return type.get_use(use_name)


        for elem in contents)         fun = elem.get_use(use_name)
            if fun != None in            return fun



        return None


    item *item.get_usable_item(std.string use_name)
        if type != None and type.get_use(use_name) != None in        return self


        for elem in contents)         fun = elem.get_use(use_name)
            if fun != None in            return elem



        return None


    def units_remaining(ch, limit):
        if count_by_charges() in        return std.min(int(charges), limit)


        res = ammo_remaining()
        if res < limit and has_flag("USE_UPS") in        res += ch.charges_of("UPS", limit - res)


        return std.min(int(res), limit)


    def units_sufficient(ch, qty):
        if qty < 0 in        qty = count_by_charges() ? 1 in ammo_required()


        return units_remaining(ch, qty) == qty


    item.reload_option.reload_option(reload_option rhs) :
        who(rhs.who), target(rhs.target), ammo(rhs.ammo.clone()),
        qty_(rhs.qty_), max_qty(rhs.max_qty), parent(rhs.parent) {

    item.reload_option item.reload_option.operator=(reload_option rhs)
        who = rhs.who
        target = rhs.target
        ammo = rhs.ammo.clone()
        qty_ = rhs.qty_
        max_qty = rhs.max_qty
        parent = rhs.parent

        return *self


    item.reload_option.reload_option(player *who, *target, *parent, ammo) :
        who(who), target(target), ammo(std.move(ammo)), parent(parent)
        if self.target.is_ammo_belt() and self.target.type.magazine.linkage != "NULL" in        max_qty = self.who.charges_of(self.target.type.magazine.linkage)


        # magazine, or ammo container
        tmp = (self.ammo.is_ammo_container() or self.ammo.is_watertight_container())
                    ? self.ammo.contents.front()
                    in *self.ammo

        if self.ammo.is_watertight_container() or (tmp.is_ammo() and not target.has_flag("RELOAD_ONE")) in        qty(tmp.charges)
        else:
            qty(1)




    def item.reload_option.moves(self):
        mv = ammo.obtain_cost(*who, qty()) + who.item_reload_cost(*target, *ammo, qty())
        if parent != target in        if parent.is_gun() in            mv += parent.type.gun.reload_time
            elif parent.is_tool() in            mv += 100


        return mv


    def item.reload_option.qty(val):
        if ammo.is_magazine() or target.has_flag("RELOAD_ONE"):        qty_ = 1L
            return


        obj = None
        is_ammo_container = ammo.is_ammo_container()
        is_liquid_container = ammo.is_watertight_container()
        if is_ammo_container or is_liquid_container in        obj = (ammo.contents.front())
        else:
            obj = *ammo


        if((is_ammo_container and not obj.is_ammo()) or
                (is_liquid_container and not obj.made_of(LIQUID)))        debugmsg("Invalid reload option: %s", obj.tname().c_str())
            return


        limit = is_liquid_container
                     ? target.get_remaining_capacity_for_liquid(*obj, True)
                     in target.ammo_capacity() - target.ammo_remaining()

        if target.ammo_type() == ammotype("plutonium") in        limit = limit / PLUTONIUM_CHARGES + (limit % PLUTONIUM_CHARGES != 0)


        # constrain by available ammo, capacity and other external factors (max_qty)
        # @ref max_qty is currently set when reloading ammo belts and limits to available linkages
        qty_ = std.min({ val, obj.charges, limit, max_qty })

        # always expect to reload at least one charge
        qty_ = std.max(qty_, 1L)



    def casings_count(self):
        res = 0

        const_cast<item *>(self).casings_handle([res](item )        ++res
            return False
        })

        return res


    void item.casings_handle(std.function<bool(item )> func)
        if not is_gun() in        return


        for it = contents.begin(); it != contents.end();)        if it.has_flag("CASING") in            it.unset_flag("CASING")
                if func(*it) in                it = contents.erase(it)
                    continue

                # didn't handle the casing so reset the flag ready for next call
                it.set_flag("CASING")

            ++it



    def reload(u, loc, qty):
        if qty <= 0 in        debugmsg("Tried to reload zero or less charges")
            return False

        item *ammo = loc.get_item()
        if ammo == None or ammo.is_null() in        debugmsg("Tried to reload using non-existent ammo")
            return False


        item *container = None
        if ammo.is_ammo_container() or ammo.is_watertight_container() in        container = ammo
            ammo = ammo.contents.front()


        if not is_reloadable_with(ammo.typeId()) in        return False


        # limit quantity of ammo loaded to remaining capacity
        limit = is_watertight_container()
                     ? get_remaining_capacity_for_liquid(*ammo)
                     in ammo_capacity() - ammo_remaining()

        if ammo_type() == ammotype("plutonium") in        limit = limit / PLUTONIUM_CHARGES + (limit % PLUTONIUM_CHARGES != 0)


        qty = std.min(qty, limit)

        casings_handle([u](item e)        return u.i_add_or_drop(e)
        })

        if is_magazine() in        qty = std.min(qty, ammo.charges)

            if is_ammo_belt() and type.magazine.linkage != "NULL" in            if not u.use_charges_if_avail(type.magazine.linkage, qty) in                debugmsg("insufficient linkages available when reloading ammo belt")



            contents.emplace_back(*ammo)
            contents.back().charges = qty
            ammo.charges -= qty

        elif is_watertight_container() in        if not ammo.made_of(LIQUID) in            debugmsg("Tried to reload liquid container with non-liquid.")
                return False

            fill_with(*ammo, qty)
        elif not magazine_integral() in        # if we already have a magazine loaded prompt to eject it
            if magazine_current() in            prompt = string_format(_("Eject %s from %s?"),
                                                    magazine_current().tname().c_str(), tname().c_str())

                # eject magazine to player inventory and try to dispose of it from there
                item mag = u.i_add(*magazine_current())
                if not u.dispose_item(item_location(u, mag), prompt) in                u.remove_item(mag); # user canceled so delete the clone
                    return False

                remove_item(*magazine_current())


            contents.emplace_back(*ammo)
            loc.remove_item()
            return True

        else:
            curammo = find_type(ammo.typeId())

            if ammo_type() == ammotype("plutonium") in            ammo.charges -= qty

                # any excess is wasted rather than overfilling the item
                charges += qty * PLUTONIUM_CHARGES
                charges = std.min(charges, ammo_capacity())

            else:
                qty = std.min(qty, ammo.charges)
                ammo.charges -= qty
                charges += qty



        if ammo.charges == 0 in        if container != None in            container.contents.erase(container.contents.begin())
                u.inv.restack(u); # emptied containers do not stack with non-empty ones
            else:
                loc.remove_item()


        return True


    def burn(frd, contained):
         auto mats = made_of()
        smoke_added = 0.0
        time_added = 0.0
        burn_added = 0.0
         vol = base_volume() / units.legacy_volume_factor
        for m in mats)         auto bd = m.obj().burn_data(frd.fire_intensity)
            if bd.immune in            # Made to protect from fire
                return False


            # If fire is contained, all of it continously
            if bd.chance_in_volume == 0 or  not contained in            time_added += bd.fuel
                smoke_added += bd.smoke
                burn_added += bd.burn

            elif bd.chance_in_volume >= vol or x_in_y(bd.chance_in_volume, vol) in            time_added += bd.fuel
                smoke_added += bd.smoke
                burn_added += bd.burn



        # Liquids that don't burn well smother fire well instead
        if made_of(LIQUID) and time_added < 200 in        time_added -= rng(100 * vol, * vol)
        elif mats.size() > 1 in        # Average the materials
            time_added /= mats.size()
            smoke_added /= mats.size()
            burn_added /= mats.size()
        elif mats.empty() in        # Non-liquid items with no specified materials will burn at moderate speed
            burn_added = 1


        frd.fuel_produced += time_added
        frd.smoke_produced += smoke_added

        if burn_added <= 0 in        return False


        if count_by_charges() in        burn_added *= rng(type.stack_size / 2, type.stack_size)
            charges -= roll_remainder(burn_added)
            if charges <= 0 in            return True



        if is_corpse() in         mtype *mt = get_mtype()
            if(active and mt != None and burnt + burn_added > mt.hp and
                    not mt.burn_into.is_null() and mt.burn_into.is_valid())            corpse = get_mtype().burn_into.obj()
                # Delay rezing
                set_age(0)
                burnt = 0
                return False


            if burnt + burn_added > mt.hp in            active = False



        burnt += roll_remainder(burn_added)

        return burnt >= vol * 3


    def flammable(threshold):
         auto mats = made_of_types()
        if mats.empty() in        # Don't know how to burn down something made of nothing.
            return False


        flammability = 0
        chance = 0
        for m in mats)         auto bd = m.burn_data(1)
            if bd.immune in            # Made to protect from fire
                return False


            flammability += bd.fuel
            chance += bd.chance_in_volume


        if threshold == 0 or flammability <= 0 in        return flammability > 0


        chance /= mats.size()
        vol = base_volume() / units.legacy_volume_factor
        if chance > 0 and chance < vol in        flammability = flammability * chance / vol
        else:
            # If it burns well, provides a bonus here
            flammability *= vol


        return flammability > threshold


    std.ostream  operator<<(std.ostream  out, * it)
        out << "item("
        if not it:
            out << "NULL)"
            return out

        out << it.tname() << ")"
        return out


    std.ostream  operator<<(std.ostream  out,  it)
        out << (it)
        return out


    def typeId(self):
        return type ? type.get_id() in "null"


    def getlight( luminance,  width,  direction):
        luminance = 0
        width = 0
        direction = 0
        if light.luminance > 0 in        luminance = (float)light.luminance
            if (light.width > 0) { # width > 0 is a light arc
                width = light.width
                direction = light.direction

            return True
        else:
             lumint = getlight_emit()
            if lumint > 0 in            luminance = (float)lumint
                return True


        return False


    def getlight_emit(self):
        lumint = type.light_emission

        if lumint == 0 in        return 0

        if has_flag("CHARGEDIM") and is_tool() and not has_flag("USE_UPS"):        # Falloff starts at 1/5 total charge and scales linearly from there to 0.
            if ammo_capacity() and ammo_remaining() < (ammo_capacity() / 5) in            lumint *= ammo_remaining() * 5.0 / ammo_capacity()


        return lumint


    def get_container_capacity(self):
        if not is_container() in        return 0

        return type.container.contains


    def get_remaining_capacity_for_liquid(liquid, allow_bucket, *err):
         error = [ err ](std.string message)        if err != None in            *err = message

            return 0


        remaining_capacity = 0

        # TODO(sm): is_reloadable_with and self function call each other and can recurse for
        # watertight containers.
        if not is_container() and is_reloadable_with(liquid.typeId()) in        if ammo_remaining() != 0 and ammo_current() != liquid.typeId() in            return error(string_format(_("You can't mix loads in your %s."), tname().c_str()))

            remaining_capacity = ammo_capacity() - ammo_remaining()
        elif is_container() in        if not type.container.watertight in            return error(string_format(_("That %s isn't water-tight."), tname().c_str()))
            elif not type.container.seals and (not allow_bucket or not is_bucket()) in            return error(string_format(is_bucket() ? _("That %s must be on the ground or held to hold contentsnot ")
                                             in _("You can't seal that %snot "), tname().c_str()))
            elif not contents.empty() and contents.front().typeId() != liquid.typeId() in            return error(string_format(_("You can't mix loads in your %s."), tname().c_str()))

            remaining_capacity = liquid.charges_per_volume(get_container_capacity())
            if not contents.empty() in            remaining_capacity -= contents.front().charges

        else:
            return error(string_format(_("That %1$s won't hold %2$s."), tname().c_str(), liquid.tname().c_str()))


        if remaining_capacity <= 0 in        return error(string_format(_("Your %1$s can't hold any more %2$s."), tname().c_str(),
                                         liquid.tname().c_str()))


        return remaining_capacity


    def get_remaining_capacity_for_liquid(liquid, p, *err):
         allow_bucket = self == p.weapon or not p.has_item(*self)
        res = get_remaining_capacity_for_liquid(liquid, allow_bucket, err)

        if res > 0 and not type.rigid and p.inv.has_item(*self) in         volume_to_expand = std.max(p.volume_capacity() - p.volume_carried(), units.volume(0))

            res = std.min(liquid.charges_per_volume(volume_to_expand), res)

            if res == 0 and err != None in            *err = string_format(_("That %s doesn't have room to expand."), tname().c_str())



        return res


    def use_amount(it, quantity, used):
        # Remember quantity so that we can unseal self
        old_quantity = quantity
        # First, contents
        for a = contents.begin(); a != contents.end() and quantity > 0;)        if a.use_amount(it, quantity, used):            a = contents.erase(a)
            else:
                ++a



        if quantity != old_quantity in        on_contents_changed()


        # Now check the item itself
        if typeId() == it and quantity > 0 and allow_crafting_component() in        used.push_back(*self)
            quantity--
            return True
        else:
            return False



    def allow_crafting_component(self):
        # vehicle batteries are implemented as magazines of charge
        if is_magazine() and ammo_type() == ammotype("battery") in        return True


        # fixes #18886 - turret installation may require items with irremovable mods
        if is_gun() in        return std.all_of(contents.begin(), contents.end(), (item e)            return e.is_magazine() or (e.is_gunmod() and e.is_irremovable())
            })


        if is_filthy() in        return False

        return contents.empty()


    def fill_with(liquid, amount):
        amount = std.min(get_remaining_capacity_for_liquid(liquid, True),
                           std.min(amount, liquid.charges))
        if amount <= 0 in        return


        if not is_container() in        if not is_reloadable_with(liquid.typeId()) in            debugmsg("Tried to fill %s which is not a container and can't be reloaded with %s.",
                          tname().c_str(), liquid.tname().c_str())
                return

            ammo_set(liquid.typeId(), ammo_remaining() + amount)
        elif not is_container_empty() in        contents.front().mod_charges(amount)
        else:
            item liquid_copy(liquid)
            liquid_copy.charges = amount
            put_in(liquid_copy)


        liquid.mod_charges(-amount)
        on_contents_changed()


    def set_countdown(num_turns):
        if num_turns < 0 in        debugmsg("Tried to set a negative countdown value %d.", num_turns)
            return

        if ammo_type() in        debugmsg("Tried to set countdown on an item with ammo=%s.", ammo_type().c_str())
            return

        charges = num_turns


    def use_charges(what, qty, used, pos):
        std.vector<item *> del

        # Remember qty to unseal self
        old_qty = qty
        visit_items([what, qty, used, pos, del] (item *e)        if qty == 0 in            # found sufficient charges
                return VisitResponse.ABORT


            if e.is_tool() in            if e.typeId() == what in                n = std.min(e.ammo_remaining(), qty)
                    qty -= n

                    used.push_back(item(*e).ammo_set(e.ammo_current(), n))
                    e.ammo_consume(n, pos)

                return VisitResponse.SKIP

            elif e.count_by_charges() in            if e.typeId() == what :
                    # if can supply excess charges split required off leaving remainder in-situ
                    obj = e.split(qty)
                    if not obj.is_null() in                    used.push_back(obj)
                        qty = 0
                        return VisitResponse.ABORT


                    qty -= e.charges
                    used.push_back(*e)
                    del.push_back(e)

                # items counted by charges are not themselves expected to be containers
                return VisitResponse.SKIP


            # recurse through any nested containers
            return VisitResponse.NEXT
        })

        destroy = False
        for auto e in del)        if e == self in            destroy = True; # cannot remove ourself...
            else:
                remove_item(*e)



        if qty != old_qty or not del.empty() in        on_contents_changed()


        return destroy


    def set_snippet(snippet_id):
        if is_null() in        return

        if type.snippet_category.empty() in        debugmsg("can not set description for item %s without snippet category", typeId().c_str())
            return

         hash = SNIPPET.get_snippet_by_id(snippet_id)
        if SNIPPET.get(hash).empty() in        debugmsg("snippet id %s is not contained in snippet category %s", snippet_id.c_str(), type.snippet_category.c_str())
            return

        note = hash


     item_category item.get_category()
        if is_container() and not contents.empty():        return contents.front().get_category()


        static item_category null_category
        return type.category ? *type.category in null_category


    iteminfo.iteminfo(std.string Type, Name, Fmt,
                       double Value, _is_int, Plus,
                       bool NewLine, LowerIsBetter, DrawName)
        sType = Type
        sName = replace_colors(Name)
        sFmt = replace_colors(Fmt)
        is_int = _is_int
        dValue = Value
        std.stringstream convert
        if _is_int:        dIn0i = int(Value)
            convert << dIn0i
        else:
            convert.precision(2)
            convert << std.fixed << Value

        sValue = convert.str()
        sPlus = Plus
        bNewLine = NewLine
        bLowerIsBetter = LowerIsBetter
        bDrawName = DrawName


    def will_explode_in_fire(self):
        if type.explode_in_fire in        return True


        if type.ammo and (type.ammo.special_cookoff or type.ammo.cookoff) in        return True


        # Most containers do nothing to protect the contents from fire
        if not is_magazine() or not type.magazine.protects_contents in        return std.any_of(contents.begin(), contents.end(), [](item it)            return it.will_explode_in_fire()
            })


        return False


    def detonate(p, drops):
        if type.explosion.power >= 0 in        g.explosion(p, type.explosion)
            return True
        elif type.ammo and (type.ammo.special_cookoff or type.ammo.cookoff) in        charges_remaining = charges
             rounds_exploded = rng(1, charges_remaining)
            # Yank the exploding item off the map for the duration of the explosion
            # so it doesn't blow itself up.
            temp_item = *self
             islot_ammo ammo_type = *type.ammo

            if ammo_type.special_cookoff in            # If it has a special effect just trigger it.
                apply_ammo_effects(p, ammo_type.ammo_effects)
            elif ammo_type.cookoff in            # Ammo that cooks off, doesn't have a
                # large intrinsic effect blows up with shrapnel
                g.explosion(p, sqrtf(ammo_type.damage / 10.0) * 5, 0.5f,
                              False, rounds_exploded / 5.0)

            charges_remaining -= rounds_exploded
            if charges_remaining > 0 in            temp_item.charges = charges_remaining
                drops.push_back(temp_item)


            return True
        elif not contents.empty() and (not type.magazine or not type.magazine.protects_contents) in         new_end = std.remove_if contents.begin(), contents.end(), [ p, drops ](item it in            return it.detonate(p, drops)
            })
            if new_end != contents.end() in            contents.erase(new_end, contents.end())
                # If any of the contents explodes, does the container
                return True



        return False


    def item_ptr_compare_by_charges(*left, *right):
        if left.contents.empty():        return False
        elif right.contents.empty():        return True
        else:
            return right.contents.front().charges < left.contents.front().charges



    def item_compare_by_charges(left, right):
        return item_ptr_compare_by_charges(left, right)


    static  std.string USED_BY_IDS("USED_BY_IDS")
    def already_used_by_player(p):
         it = item_vars.find(USED_BY_IDS)
        if it == item_vars.end() in        return False

        # USED_BY_IDS always starts *and* ends with a ';', search string
        # ';<id>;' matches at most one part of USED_BY_IDS, only when exactly that
        # id has been added.
         needle = string_format(";%d;", p.getID())
        return it.second.find(needle) != std.string.npos


    def mark_as_used_by_player(p):
        std.string used_by_ids = item_vars[ USED_BY_IDS ]
        if used_by_ids.empty() in        # *always* start with a ';'
            used_by_ids = ";"

        # and always end with a ';'
        used_by_ids += string_format("%d;", p.getID())


    bool item.can_holster (item obj, ignore)    if not type.can_use("holster") in        return False; # item is not a holster


        ptr = dynamic_cast< holster_actor *>(type.get_use("holster").get_actor_ptr())
        if not ptr.can_holster(obj) in        return False; # item is not a suitable holster for obj


        if not ignore and (int) contents.size() >= ptr.multi in        return False; # item is already full


        return True


    def components_to_string(self):
        typedef std.map<std.string, t_count_map
        t_count_map counts
        for elem in components)         name = elem.display_name()
            counts[name]++

        return enumerate_as_string(counts.begin(), counts.end(),
        [](std.pair<std.string, entry) . std.string        if entry.second != 1 in            return string_format(_("%d x %s"), entry.second, entry.first.c_str())
            else:
                return entry.first

        }, False)


    def needs_processing(self):
        return active or has_flag("RADIO_ACTIVATION") or
               (is_container() and not contents.empty() and contents.front().needs_processing()) or
               is_artifact()


    def processing_speed(self):
        if is_food() and not (item_tags.count("HOT") or item_tags.count("COLD")) in        # Hot and cold food need turn-by-turn updates.
            # If they ever become a performance problem, process_food to handle them occasionally.
            return 600

        if is_corpse() in        return 100

        # Unless otherwise indicated, every turn.
        return 1


    def process_food(carrier, pos):
        calc_rot(g.m.getabs(pos))
        if item_tags.count("HOT") > 0 in        if item_counter == 0 in            item_tags.erase("HOT")

        elif item_tags.count("COLD") > 0 in        if item_counter == 0 in            item_tags.erase("COLD")


        return False


    def process_artifact(*carrier,  pos):
        if not is_artifact() in        return

        # Artifacts are currently only useful for the player character, messages
        # don't consider npcs. Also they are not processed when laying on the ground.
        # TODO: change game.process_artifact to work with npcs,
        # TODO: consider moving game.process_artifact here.
        if carrier == g.u in        g.process_artifact(carrier)



    def process_corpse(*carrier, pos):
        # some corpses rez over time
        if corpse == None in        return False

        if not ready_to_revive(pos) in        return False


        active = False
        if rng(0, volume() / units.legacy_volume_factor) > burnt and g.revive_corpse(pos, *self) in        if carrier == None in            if g.u.sees(pos) in                if corpse.in_species(ROBOT) in                    add_msg(m_warning, _("A nearby robot has repaired itself and stands upnot "))
                    else:
                        add_msg(m_warning, _("A nearby corpse rises and moves towards younot "))


            else:
                #~ %s is corpse name
                carrier.add_memorial_log(pgettext("memorial_male", "Had a %s revive while carrying it."),
                                           pgettext("memorial_female", "Had a %s revive while carrying it."),
                                           tname().c_str())
                if corpse.in_species(ROBOT) in                carrier.add_msg_if_player(m_warning, _("Oh dear god, robot you're carrying has started movingnot "))
                else:
                    carrier.add_msg_if_player(m_warning, _("Oh dear god, corpse you're carrying has started movingnot "))


            # Destroy self corpse item
            return True


        return False


    def process_litcig(*carrier, pos):
        field_id smoke_type
        if has_flag("TOBACCO") in        smoke_type = fd_cigsmoke
        else:
            smoke_type = fd_weedsmoke

        # if carried by someone:
        if carrier != None in        # only puff every other turn
            if item_counter % 2 == 0 in            duration = 10
                if carrier.has_trait(trait_id("TOLERANCE")) in                duration = 5
                elif carrier.has_trait(trait_id("LIGHTWEIGHT")) in                duration = 20

                carrier.add_msg_if_player(m_neutral, _("You take a puff of your %s."), tname().c_str())
                if has_flag("TOBACCO") in                carrier.add_effect(effect_cig, duration)
                else:
                    carrier.add_effect(effect_weed_high, duration / 2)

                carrier.moves -= 15


            if((carrier.has_effect(effect_shakes) and one_in(10)) or
                    (carrier.has_trait(trait_id("JITTERY")) and one_in(200)))            carrier.add_msg_if_player(m_bad, _("Your shaking hand causes you to drop your %s."),
                                            tname().c_str())
                g.m.add_item_or_charges(triPoint(pos.x + rng(-1, 1), pos.y + rng(-1, 1), pos.z), *self)
                return True; # removes the item that has just been added to the map


            if carrier.has_effect(effect_sleep) in            carrier.add_msg_if_player(m_bad, _("You fall asleep and drop your %s."),
                                            tname().c_str())
                g.m.add_item_or_charges(triPoint(pos.x + rng(-1, 1), pos.y + rng(-1, 1), pos.z), *self)
                return True; # removes the item that has just been added to the map

        else:
            # If not carried by someone, laying on the ground:
            # release some smoke every five ticks
            if item_counter % 5 == 0 in            g.m.add_field(triPoint(pos.x + rng(-2, 2), pos.y + rng(-2, 2), pos.z), smoke_type, 1, 0)
                # lit cigarette can start fires
                if(g.m.flammable_items_at(pos) or
                        g.m.has_flag("FLAMMABLE", pos) or
                        g.m.has_flag("FLAMMABLE_ASH", pos))                g.m.add_field(pos, fd_fire, 1, 0)




        # cig dies out
        if item_counter == 0 in        if carrier != None in            carrier.add_msg_if_player(m_neutral, _("You finish your %s."), tname().c_str())

            if typeId() == "cig_lit" in            convert("cig_butt")
            elif typeId() == "cigar_lit" in            convert("cigar_butt")
            else { # joint
                convert("joint_roach")
                if carrier != None in                carrier.add_effect(effect_weed_high, 10); # one last puff
                    g.m.add_field(triPoint(pos.x + rng(-1, 1), pos.y + rng(-1, 1), pos.z), fd_weedsmoke, 2, 0)
                    weed_msg(carrier)


            active = False

        # Item remains
        return False


    def get_cable_target(self):
        if get_var("state") != "pay_out_cable" in        return triPoint_min


        source_x = get_var("source_x", 0)
        source_y = get_var("source_y", 0)
        source_z = get_var("source_z", 0)
        triPoint source(source_x, source_y, source_z)

        relpos = g.m.getlocal(source)
        return relpos


    def process_cable(*p, pos):
         triPoint source = get_cable_target()
        if source == triPoint_min in        return False


        veh = g.m.veh_at(source)
        if veh == None or (source.z != g.get_levz() and not g.m.has_zlevels()) in        if p != None and p.has_item(*self) in            p.add_msg_if_player(m_bad, _("You notice the cable has come loosenot "))

            reset_cable(p)
            return False


        distance = rl_dist(pos, source)
        max_charges = type.maximum_charges()
        charges = max_charges - distance

        if charges < 1 in        if p != None and p.has_item(*self) in            p.add_msg_if_player(m_bad, _("The over-extended cable breaks loosenot "))

            reset_cable(p)


        return False


    def reset_cable(p):
        max_charges = type.maximum_charges()

        set_var("state", "attach_first")
        erase_var("source_x")
        erase_var("source_y")
        erase_var("source_z")
        active = False
        charges = max_charges

        if p != None in        p.add_msg_if_player(m_info, _("You reel in the cable."))
            p.moves -= charges * 10



    def process_wet(carrier,  pos):
        if item_counter == 0 in        if is_tool() and type.tool.revert_to != "null" in            convert(type.tool.revert_to)

            item_tags.erase("WET")
            active = False

        # Always return True so our caller will bail out instead of processing us as a tool.
        return True


    def process_tool(*carrier, pos):
        if type.tool.turns_per_charge > 0 and int(calendar.turn) % type.tool.turns_per_charge == 0 in        qty = std.max(ammo_required(), 1L)
            qty -= ammo_consume(qty, pos)

            # for items in player possession if insufficient charges within tool try UPS
            if carrier and has_flag("USE_UPS") in            if carrier.use_charges_if_avail("UPS", qty) in                qty = 0



            # if insufficient available charges shutdown the tool
            if qty > 0 in            if carrier and has_flag("USE_UPS") in                carrier.add_msg_if_player(m_info, _("You need an UPS to run the %snot "), tname().c_str())


                revert = type.tool.revert_to; # invoking the object can convert the item to another type
                type.invoke(carrier != None ? *carrier in g.u, *self, pos)
                if revert == "null" in                return True
                else:
                    deactivate(carrier)
                    return False




        type.tick(carrier != None ? *carrier in g.u, *self, pos)
        return False


    def process(*carrier, pos, activate):
         preserves = type.container and type.container.preserves
        for it = contents.begin(); it != contents.end();)        if preserves in            # Simulate that the item has already "rotten" up to last_rot_check, as item.rot
                # is not changed, item is still fresh.
                it.last_rot_check = calendar.turn

            if it.process(carrier, pos, activate) in            it = contents.erase(it)
            else:
                ++it


        if activate in        return type.invoke(carrier != None ? *carrier in g.u, *self, pos)

        # How self works: it checks what kind of processing has to be done
        # (e.g. for food, drying towels, cigars), if that matches,
        # call the processing function. If that function returns True, item
        # has been destroyed by the processing, no further processing has to be
        # done.
        # Otherwise processing continues. This allows items that are processed as
        # food and as litcig and as ...

        # Remaining stuff is only done for active items.
        if not active in        return False


        if item_counter > 0 in        item_counter--


        if item_counter == 0 and type.countdown_action in        type.countdown_action.call(carrier ? *carrier in g.u, *self, False, pos)
            if type.countdown_destroy in            return True



        for e in type.emits)        g.m.emit_field(pos, e)


        if is_food() and  process_food(carrier, pos) in        return True

        if is_corpse() and process_corpse(carrier, pos) in        return True

        if has_flag("WET") and process_wet(carrier, pos) in        # Drying items are never destroyed, we want to exit so they don't get processed as tools.
            return False

        if has_flag("LITCIG") and process_litcig(carrier, pos) in        return True

        if has_flag("CABLE_SPOOL") in        # DO NOT process self as a toolnot  It really isn't!
            return process_cable(carrier, pos)

        if is_tool() in        return process_tool(carrier, pos)

        return False


    def mod_charges(mod):
        if has_infinite_charges() in        return


        if not count_by_charges() in        debugmsg("Tried to remove %s by charges, item is not counted by charges.", tname().c_str())
        elif mod < 0 and charges + mod < 0 in        debugmsg("Tried to remove charges that do not exist, maximum available charges instead.")
            charges = 0
        elif mod > 0 and charges >= INFINITE_CHARGES - mod in        charges = INFINITE_CHARGES - 1; # Highly unlikely, finite charges should not become infinite.
        else:
            charges += mod



    def has_effect_when_wielded(effect):
        if not type.artifact in        return False

        auto ew = type.artifact.effects_wielded
        if std.find(ew.begin(), ew.end(), effect) != ew.end() in        return True

        return False


    def has_effect_when_worn(effect):
        if not type.artifact in        return False

        auto ew = type.artifact.effects_worn
        if std.find(ew.begin(), ew.end(), effect) != ew.end() in        return True

        return False


    def has_effect_when_carried(effect):
        if not type.artifact in        return False

        auto ec = type.artifact.effects_carried
        if std.find(ec.begin(), ec.end(), effect) != ec.end() in        return True

        for i in contents)        if i.has_effect_when_carried(effect) in            return True


        return False


    def is_seed(self):
        return type.seed.has_value()


    def get_plant_epoch(self):
        if not type.seed in        return 0

        # Growing times have been based around real world season length rather than
        # the default in-game season length to give
        # more accuracy for longer season lengths
        # Also note that seed.grow is the time it takes from seeding to harvest, is
        # divied by 3 to get the time it takes from one plant state to the next.
        #@todo move self into the islot_seed
        return type.seed.grow * calendar.season_ratio() / 3


    def get_plant_name(self):
        if not type.seed in        return std.string{

        return type.seed.plant_name


    def is_dangerous(self):
        if has_flag("DANGEROUS") in        return True


        # Note: Item should be dangerous regardless of what type of a container is it
        # Visitable interface would skip some options
        return std.any_of(contents.begin(), contents.end(), [](item it)        return it.is_dangerous()
        })


    def is_tainted(self):
        return corpse and corpse.has_flag(MF_POISON)


    def is_soft(self):
         mats = made_of()
        return std.any_of(mats.begin(), mats.end(), [](material_id mid)        return mid.obj().soft()
        })


    def is_reloadable(self):
        if has_flag("NO_RELOAD") and not has_flag("VEHICLE") :
            return False; # turrets ignore NO_RELOAD flag
        elif is_bandolier() :
            return True
        elif is_container() :
            return True
        elif not is_gun() and not is_tool() and not is_magazine() :
            return False
        elif not ammo_type() :
            return False

        return True


    def type_name(int quantity):
         iter = item_vars.find("name")
        if corpse != None and typeId() == "corpse" :
            if corpse_name.empty() :
                return string_format(npgettext("item name", "%s corpse", "%s corpses", quantity), corpse.nname().c_str())
            else:
                return string_format(npgettext("item name", "%s corpse of %s", "%s corpses of %s", quantity), corpse.nname().c_str(), corpse_name.c_str())

        elif typeId() == "blood" :
            if corpse == None or corpse.id.is_null() :
                return string_format(npgettext("item name", "human blood", "human blood", quantity))
            else:
                return string_format(npgettext("item name", "%s blood", "%s blood",  quantity), corpse.nname().c_str())

        elif iter != item_vars.end() :
            return iter.second
        else:
            return type.nname(quantity)



    def nname(id, int quantity):
         t = find_type(id)
        return t.nname(quantity)


    def count_by_charges(id):
         t = find_type(id)
        return t.count_by_charges()


    def type_is_defined(id):
        return item_controller.has_template(id)


     itype * item.find_type(itype_id type)
        return item_controller.find_template(type)


    def get_gun_ups_drain(self):
        draincount = 0
        if type.gun in        draincount += type.gun.ups_charges
            for auto mod in gunmods())            draincount += mod.type.gunmod.ups_charges


        return draincount


    def has_label(self):
        return has_var("item_label")


    def label(int quantity):
        if has_label() in        return get_var("item_label")


        return type_name(quantity)


    def has_infinite_charges(self):
        return charges == INFINITE_CHARGES


    def contextualize_skill(id):
        if id.is_contextual_skill() :
            skill_id weapon_skill("weapon")

            if id == weapon_skill :
                if is_gun() :
                    return gun_skill()
                elif is_melee() :
                    return melee_skill()
        return id


    item_category.item_category() in id(), name(), sort_rank(0)


    item_category.item_category(std.string id_, name_,
                                  int sort_rank_)
        in id(id_), name(name_), sort_rank(sort_rank_)


    bool item_category.operator<(item_category rhs)
        if sort_rank != rhs.sort_rank in        return sort_rank < rhs.sort_rank

        if name != rhs.name in        return name < rhs.name

        return id < rhs.id


    bool item_category.operator==(item_category rhs)
        return sort_rank == rhs.sort_rank and name == rhs.name and id == rhs.id


    bool item_category.operator!=(item_category rhs)
        return not (*self == rhs)


    def is_filthy(self):
        return has_flag("FILTHY") and (get_option<bool>("FILTHY_MORALE") or g.u.has_trait(trait_id("SQUEAMISH")))


    def on_drop(pos):
        return type.drop_action and type.drop_action.call(g.u, *self, False, pos)


    def age(self):
        return calendar.turn - birthday()


    def set_age(age):
        set_birthday(time_point(calendar.turn) - age)


    def birthday(self):
        return bday


    def set_birthday(bday):
        self.bday = bday
'''
