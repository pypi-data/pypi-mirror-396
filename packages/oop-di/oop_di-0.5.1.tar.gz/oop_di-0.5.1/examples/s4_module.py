from abc import ABC, abstractmethod


class MailerInterface(ABC):
    @abstractmethod
    def send_mail(self) -> None:
        ...


class Mailer(MailerInterface):
    def __init__(self, from_email: str) -> None:
        self.from_email = from_email

    def send_mail(self) -> None:
        print(f"Sending from {self.from_email}...")
        print("Sent")


class MultiMailer(MailerInterface):
    def __init__(self, mailers: list[MailerInterface]) -> None:
        self.mailers = mailers

    def send_mail(self) -> None:
        for mailer in self.mailers:
            mailer.send_mail()


class ProductService:
    def __init__(self, mailer: MailerInterface) -> None:
        self.mailer = mailer

    def process_product(self) -> None:
        print("processing product")
        self.mailer.send_mail()
