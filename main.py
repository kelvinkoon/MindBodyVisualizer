from mindbody_client import MindBodyClient


def main():
    client = MindBodyClient()
    client.createClassCsv()

if __name__=="__main__":
    main()