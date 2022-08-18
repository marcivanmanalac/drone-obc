from sys import path as sysPath
from os import path as osPath
# from utils import Role
from Link.link import Link
# from Studio.studio import Studio
from time import sleep
from Link.link_LED import LinkLED


filepath = osPath.dirname(osPath.realpath(__file__))
sysPath.append(filepath + "/DDS_connector")
import rticonnextdds_connector as rti


if __name__ == "__main__":
    # role = Role.LINK

    REPLICATE = 1
    EMULATE_DRONE_NETWORK = 1
    # DIAGNOSIS_LOGIC = 0
    # REQUEST_ID_GM1 = 0
    # REQUEST_MAINTENANCE_FILE = 1

    # DDS init
    print(filepath + "/Internest.xml")

    network_interface_available = False
    while not network_interface_available:
        try:
            connector = rti.Connector("MyParticipantLibrary::Zero", filepath + "/Internest.xml")
            network_interface_available = True
        except:
            print("Interface unavailable  - Impossible to start DDS service")
            sleep(2)
            continue

    # if not DIAGNOSIS_LOGIC:

    # if role == Role.LINK:
    link = Link(REPLICATE, EMULATE_DRONE_NETWORK, connector)
    led = LinkLED()
    # link.link_main_loop()
    while True:
        link.reset_requests()
        led.start_blink(0)
        # suppression de tous les fichies qui pourraient encore être présents
        link.clean_directories()
        # poll lolas for node declaration at connection time
        print("Polling network...")
        while not link.pollNetwork():
            sleep(5)
        print("Waiting for mode requests from Studio")
        while not link.configuration_requested and not link.diag_requested and not link.reset:
            link.parse_commands()
        if link.reset:
            print("Link reset requested by studio")
        elif link.configuration_requested:
            link.reset_requests()
            print("Entering configuration mode")
            # send another ping request to change lolas ground sub mode
            link.send_ping()
            # then poll lolas for configuration
            print("Polling configuration...")
            while not link.pollForConfiguration():
                sleep(0.5)
            # génération du fichier de configuration
            link.generate_current_configuration_file()
            # todo : génération du fichier de maintenance
            while True:
                # attente d'une nouvelle configuration ou d'une commande reset(bloquant)
                print("No new configuration and no reset, waiting...")
                while not link.reset and not link.handle_new_configuration():
                    link.parse_commands()

                if link.reset:
                    print("Link reset requested by studio")
                    break
                # suppression de tous les fichiers qui pourraient encore être présents
                link.clean_directories()
                led.stop_blinking()
                led.reset()
                led.start_blink(1)
                # Transfert de la nouvelle configuration vers LoLas
                link.transfer_new_configuration()
                sleep(0.5)
                # Then poll again to read the deployed configuration back again
                print("Checking configuration...")
                while not link.pollForConfiguration():
                    sleep(0.5)
                # génération du fichier de configuration
                link.generate_current_configuration_file()
                # attente pour permettre à Studio de récupérer le fichier
                sleep(2)
                led.stop_blinking()
                led.reset()
                led.start_blink(0)
        elif link.diag_requested:
            link.reset_requests()
            print("Entering diag mode")
            # send ack message to change lolas mode from GROUND / GROUND IDLE to ENABLED
            link.send_empty_ack()

            is_streaming = False
            while True:
                link.parse_commands()
                if link.shall_stream:
                    is_streaming = True
                    # link.send_fake_diag_measures()
                    # todo récupérer les messages 3D pos et status
                    link.getDiagnosisMessages()
                    # todo encapsuler dans des trames DDS pour envoi vers
                    link.broadcast_diag_samples()
                    sleep(0.1)
                if is_streaming and not link.shall_stream:
                    print("Stopping data streaming")
                    is_streaming = False
                if link.reset:
                    print("Link reset requested by studio")
                    break  # exit the while loop here

        link.reset_requests()
        led.stop_blinking()
        led.reset()
        # todo verifier si on revient à l'étape de polling ou plutôt au while
