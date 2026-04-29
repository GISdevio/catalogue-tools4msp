#!/bin/bash
cd /mnt/tools4msp/ckan
echo "Starting spambot cleanup..."

# Pharmaceutical spam
for user in alprazolamfarmacia518 bromazepamfarmacia422 diazepamfarmacia913 imovanefarmacia129 lorazepamfarmacia648 lyrica153 tramadolofarmacia837 zolpidemfarmacia943; do
    echo "Deleting user: $user"
    docker compose exec -T ckan ckan -c /etc/ckan/production.ini user remove "$user" 2>/dev/null && echo "✓ Deleted: $user" || echo "✗ Failed: $user"
done

# Gambling spam  
for user in agenplacebet boplacebet judi-online koigamesseru linkplacebet linkplacebet138 mainplacebet placebet placebet- placebet-138 placebetlink raja138 sabung-ayam-online situsplacebet situs-slot-gacor slotmaxwingacor; do
    echo "Deleting user: $user"
    docker compose exec -T ckan ckan -c /etc/ckan/production.ini user remove "$user" 2>/dev/null && echo "✓ Deleted: $user" || echo "✗ Failed: $user"
done

# Suspicious numbered accounts
for user in 0025849018 0258049018 036u849018 06621849018 11202849018 1124ju849018 1211ju849018 12284901802 20250849018 2029p249018 2036u849018 205205887 21011149018 210221ju849018 21022849018 21024ju849018 21055u849018 2112u849018 21152049018 212026649018 2121002249018 21ju21002218 220555849018 2210559018 22122u849018 22184901802 247098922shua22 2501849018 25206922shua22 3550849018 36804u849018 369u849018 38802335200 399acju849018 4571849018 5880u849018 a3505887 aa02e849018 cs0gg849018 sc2020181820; do
    echo "Deleting user: $user"
    docker compose exec -T ckan ckan -c /etc/ckan/production.ini user remove "$user" 2>/dev/null && echo "✓ Deleted: $user" || echo "✗ Failed: $user"
done

# Pattern-based spam
for user in demon qq xlauraxx1 rose prenses mendoan01 mendoan02 dota88moi kucingungu pagianime sidisdih mario sasa; do
    echo "Deleting user: $user"
    docker compose exec -T ckan ckan -c /etc/ckan/production.ini user remove "$user" 2>/dev/null && echo "✓ Deleted: $user" || echo "✗ Failed: $user"
done

# Additional suspicious accounts
for user in askme66 jessutarman jovianas2 julian13 mark01 mark02 mark03 mark04 mark05 yatiningsih attard ayah burcu bwang caca crich dians201 dians202 dians203 dians204 dians205 dians206 eliyanaahri febridrianto fghj hngnh itil andrewbutstay aqsin elida321; do
    echo "Deleting user: $user"
    docker compose exec -T ckan ckan -c /etc/ckan/production.ini user remove "$user" 2>/dev/null && echo "✓ Deleted: $user" || echo "✗ Failed: $user"
done

# Generic test patterns
for user in aanjau abnjau adebebel fdebebel hebebel lebebel rdebebel tdebebel vebebel webebel fatete jatete matete qatete tatete beang ceeang eeeang qeeang seeang yeeang beemel eeemel ghemel heemel keemel leemel memel peemel remel semel bodrer doler woler zoler gurte jkeurte reurte teurte turte deacorsse qdacorsse rdacorsse reacorsse teacorsse yeacorsse ydacorsse weyah yeyah reweyah teweyah vbeyah qweyah reyah meyah leyah eeweyah; do
    echo "Deleting user: $user"
    docker compose exec -T ckan ckan -c /etc/ckan/production.ini user remove "$user" 2>/dev/null && echo "✓ Deleted: $user" || echo "✗ Failed: $user"
done

echo "Spambot cleanup completed!"