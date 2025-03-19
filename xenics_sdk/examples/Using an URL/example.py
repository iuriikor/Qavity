import sys
from xenics.xeneth import XCamera
from xenics.xeneth.errors import XenethAPIException

def main():
    """ 
    Let's assume we got two cameras on the network using a fixed IP.
    We are aware of which IPs they have, the first one is on 192.168.1.87 and we know it is a Gobi-640 GigE camera. 
    The second camera has IP address 192.168.1.210 and we know it's a Gobi384PDCLSCI50 using the Xenics network protocol (XNP)
    """
    
    print("Opening connections.")
    cam1 = XCamera()
    cam2 = XCamera()

    try:
        cam1.open("gev://192.168.1.110")   # following GigEVision URL scheme
        cam2.open("xnp://192.168.1.210")  # following Xeneth network protocol URL scheme

        if cam1.is_initialized:
            print("Cam1 initialized.")
        else:
            print("Cam1 not found.")

        if cam2.is_initialized:
            print("Cam2 initialized")
        else:
            print("Cam2 not found.")

        
    except XenethAPIException as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleanup.")

        # close handles
        if cam1.is_initialized:
            cam1.close()
        if cam2.is_initialized:
            cam2.close()

if __name__ == "__main__":
    main()
