# nosec B311 - Random is used for mock data generation, not security
import logging
import os
import random
import time
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from djangoldp_dataspace_democracy.models import *
from mistralai import Mistral

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populates the database with mock data."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.last_call_time = 0

    def generate_text(self, prompt):
        current_time = time.time()
        if self.last_call_time > 0:
            elapsed = current_time - self.last_call_time
            if elapsed < 1:
                time.sleep(1 - elapsed)
        self.last_call_time = time.time()
        if not self.client:
            api_key = os.environ.get("MISTRAL_API_KEY")
            if not api_key:
                logger.error("MISTRAL_API_KEY environment variable not set.")
                return "Sample text"
            self.client = Mistral(api_key=api_key)

        try:
            messages = [
                {
                    "role": "system",
                    "content": "Tu aides à la création de données de test pour le projet Dataspace Democracy. Reste concis, ne dis rien de plus que la réponse à la question. Ne donne qu'une réponse, ne formule pas d'hypothèse, n'utilise pas de mise en forme.",
                },
                {"role": "user", "content": prompt},
            ]
            response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip().strip('"')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Error generating text: {e}"))
            return "Sample text"

    def handle(self, *args, **options):
        """
        Create some Organizations, Participatory Spaces, Proposals and Comments

        At least 10 Organizations, 20 Participatory Spaces, 100 Proposals and 200 Comments should be made
        """
        self.stdout.write("Creating mock data...")

        # Create OrganizationTypes
        org_types = []
        type_names = [
            "Non Profit",
            "Gouvernment",
            "Entreprise privée",
            "NGO",
            "Association",
        ]
        for name in type_names:
            org_type, created = OrganizationType.objects.get_or_create(name=name)
            org_types.append(org_type)

        # Create Tags for expertise domains
        tags = []
        tag_names = [
            "Environnement",
            "Éducation",
            "Santé",
            "Technologie",
            "Economie",
            "Culture",
            "Sports",
            "Politique",
        ]
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            tags.append(tag)

        # Create Locations
        locations = []
        cities = [
            "Paris",
            "Lyon",
            "Marseille",
            "Toulouse",
            "Nice",
            "Nantes",
            "Strasbourg",
            "Montpellier",
        ]
        for city in cities:
            location = Location.objects.create(
                streetAddress=f"{random.randint(1, 100)} rue de la Paix",
                addressLocality=city,
                postalCode=f"{random.randint(10000, 99999)}",
                addressCountry="France",
            )
            locations.append(location)

        # Create Organizations
        organizations = []
        for i in range(10):
            org_type = random.choice(org_types)
            expertises = random.sample(tags, random.randint(0, 3))
            location = random.choice(locations)
            description = self.generate_text(
                f"Génère une courte description pour une organisation qui s'inscrit dans le cadre d'une plateforme de participation citoyenne. Ne précise pas son nom. C'est {org_type.name} basée à {location.addressCountry}. Elle a pour expertise {', '.join([t.name for t in expertises])}."
            )
            name = self.generate_text(
                f"Génère un nom pour une organisation décrite comme '{description}'. Ce nom doit être unique, signficatif, impactant."
            ).strip(".")

            org = Organization.objects.create(
                name=name,
                description=description,
                logo=f"https://placehold.in/{random.randint(30, 100)}x{random.randint(30, 100)}",
                website=f"https://example{random.randint(1, 100)}.com",
                email=f"contact@{name.lower().replace(' ', '')}.com",
                organization_type=org_type,
                location=location,
            )
            # Add random expertise domains
            org.expertise_domains.set(expertises)
            organizations.append(org)

        # Create Participatory Spaces
        participatory_spaces = []
        for i in range(20):
            organizer = random.choice(organizations)
            start_date = datetime.now() + timedelta(days=random.randint(-30, 30))
            end_date = start_date + timedelta(days=random.randint(1, 30))
            description = self.generate_text(
                f"Génère une courte description pour un Participatory Space organisé par '{organizer.name}' dans le cadre d'une plateforme de participation citoyenne. Ce Participatory Space peut représenter une Assemblée, une Conférence, un Processus de décision, etc. Il a lieu à {organizer.location.addressCountry}. Il aura lieu entre le {start_date} et le {end_date}. Il y sera abordé des sujets comme {', '.join([t.name for t in random.sample(tags, 2)])}."
            )
            name = self.generate_text(
                f"Genère un nom pour un Participatory Space organisé décrit comme '{description}'. Un Participatory Space peut représenter une Assemblée, une Conférence, un Processus de décision, etc. dans le cadre d'une plateforme de participation citoyenne. Ce nom doit être unique, signficatif, impactant."
            ).strip(".")

            ps = ParticipatorySpace.objects.create(
                name=name,
                description=description,
                banner=f"https://placehold.in/{random.randint(200, 400)}x{random.randint(100, 200)}",
                start_date=start_date,
                end_date=end_date,
                organizer=organizer,
                location=Location.objects.create(
                    streetAddress=f"{random.randint(1, 100)} avenue des Participations",
                    addressLocality=organizer.location.addressLocality,
                    postalCode=organizer.location.postalCode,
                    addressCountry=organizer.location.addressCountry,
                ),
            )
            participatory_spaces.append(ps)

        # Create Persons
        persons = []
        for i in range(50):
            first_name = random.choice(
                [
                    "Léa",
                    "Marie",
                    "Jean",
                    "Pierre",
                    "Julie",
                    "Alexandre",
                    "Sébastien",
                    "Camille",
                    "Léo",
                    "Sophie",
                    "Charlotte",
                    "Matthieu",
                    "Laurie",
                    "Bastien",
                    "Raphaël",
                    "Adèle",
                    "Hugo",
                    "Louise",
                    "Gabrielle",
                    "Paul",
                    "Anaïs",
                    "Thibaut",
                    "Clément",
                    "Élise",
                    "Vincent",
                    "Alice",
                    "Émile",
                    "Florian",
                    "Victoire",
                    "Léonie",
                    "Arthur",
                    "Justine",
                    "Laurène",
                    "Cécile",
                    "Étienne",
                    "Fanny",
                    "Gaspard",
                    "Hélène",
                    "Mélanie",
                    "Nathalie",
                    "Olivier",
                    "Pascal",
                    "Romain",
                    "Sandrine",
                    "Sylvie",
                    "Stéphanie",
                    "Tiphaine",
                    "Valérie",
                    "Yann",
                    "Yolande",
                ]
            )
            last_name = random.choice(
                [
                    "Dupont",
                    "Durand",
                    "Martin",
                    "Bertrand",
                    "Moreau",
                    "Lefebvre",
                    "Dupuis",
                    "Garnier",
                    "Girard",
                    "Lemarchand",
                    "Lefort",
                    "Lemaire",
                    "Leroy",
                    "Leroux",
                    "Lévêque",
                    "Maillet",
                    "Malard",
                    "Marchand",
                    "Marc",
                    "Marquet",
                    "Maurice",
                    "Méchin",
                    "Mercier",
                    "Michaud",
                    "Millet",
                    "Monnet",
                    "Montagne",
                    "Montel",
                    "Morel",
                    "Morin",
                    "Moulin",
                    "Muller",
                    "Munier",
                    "Nadeau",
                    "Navarro",
                    "Nicolas",
                    "Nicol",
                    "Noël",
                    "Normand",
                    "Oger",
                    "Olivier",
                    "Paquet",
                    "Pascal",
                    "Patin",
                    "Paturel",
                    "Péchard",
                    "Périer",
                    "Perrin",
                    "Petit",
                    "Philippe",
                    "Pierrard",
                    "Pillard",
                    "Pillet",
                    "Piquet",
                    "Pitoux",
                    "Plessis",
                    "Poidevin",
                    "Poisson",
                    "Pommier",
                    "Portier",
                    "Potier",
                    "Poulin",
                    "Poulain",
                    "Poupart",
                    "Prévost",
                    "Provost",
                    "Quentin",
                    "Rabier",
                    "Racine",
                    "Raffin",
                    "Ragot",
                    "Raison",
                    "Ramond",
                    "Renaud",
                    "René",
                    "Ricard",
                    "Rivière",
                    "Robert",
                    "Robin",
                    "Roger",
                    "Rolland",
                    "Romain",
                    "Rousseau",
                    "Roussel",
                    "Roux",
                    "Roy",
                    "Royer",
                    "Ruiz",
                    "Rusch",
                    "Sagnard",
                    "Sallé",
                    "Sanson",
                    "Sauvage",
                    "Savary",
                    "Scherer",
                    "Schmid",
                    "Schneider",
                    "Schmitt",
                    "Schnitzler",
                    "Schreiber",
                    "Schulz",
                    "Schuster",
                    "Schwarz",
                    "Scott",
                    "Séguin",
                    "Séguier",
                    "Selle",
                    "Séna",
                    "Sénéchal",
                    "Sénecal",
                    "Serrand",
                    "Serrano",
                    "Seyfried",
                    "Seymour",
                    "Seynat",
                    "Seyrig",
                    "Seyve",
                    "Simonet",
                    "Simon",
                    "Simonet",
                    "Simpson",
                    "Sineau",
                    "Siret",
                    "Sirois",
                    "Sivignon",
                    "Slama",
                    "Soler",
                    "Solère",
                    "Sommier",
                    "Sorel",
                    "Sorin",
                    "Soulier",
                    "Sourice",
                    "Soyer",
                    "Stabile",
                    "Stauffer",
                    "Stein",
                    "Steinmetz",
                    "Stenger",
                    "Stévenin",
                    "Stévenot",
                    "Stier",
                    "Stolz",
                    "Stoltz",
                    "Stora",
                    "Stoskopf",
                    "Strubel",
                    "Stuck",
                    "Stutzmann",
                    "Sudres",
                    "Sueur",
                    "Sugier",
                    "Sulpice",
                    "Sureau",
                    "Surmont",
                    "Sutter",
                    "Swan",
                    "Taillefer",
                    "Talbot",
                    "Tanguy",
                    "Tardif",
                    "Tassin",
                    "Tavernier",
                    "Tchanon",
                    "Teissier",
                    "Tellier",
                    "Terret",
                    "Terrien",
                    "Tesson",
                    "Thébault",
                    "Théodore",
                    "Thévenin",
                    "Thévenot",
                    "Thibaut",
                    "Thibert",
                    "Thierry",
                    "Thillot",
                    "Thimonier",
                    "Thiriet",
                    "Thivierge",
                    "Thomas",
                    "Thomassin",
                    "Thouvenin",
                    "Thouvenot",
                    "Tiberghien",
                    "Tournemire",
                    "Tournier",
                    "Tournois",
                    "Tourte",
                    "Tourvieille",
                    "Tranchant",
                    "Tricot",
                    "Triquet",
                    "Trochet",
                    "Trottier",
                    "Trouillard",
                    "Trouvé",
                    "Tubert",
                    "Turc",
                    "Turmel",
                    "Turpin",
                    "Turquet",
                    "Tutard",
                    "Tutelle",
                ]
            )
            name = f"{first_name} {last_name}"
            person = Person.objects.create(
                name=name,
                homepage=f"https://placehold.in/{random.randint(30, 100)}x{random.randint(30, 100)}",
                depiction=f"https://placehold.in/{random.randint(30, 100)}x{random.randint(30, 100)}",
                profile_url=f"https://profile{random.randint(1, 100)}.com",
            )
            persons.append(person)

        # Create Meetings
        meetings = []
        for i in range(20):
            location = random.choice(locations)
            name = self.generate_text(
                f"Génère un nom pour une rencontre ou une réunion à {location.addressCountry}, il y sera question de {', '.join([t.name for t in random.sample(tags, 2)])} dans le cadre d'une plateforme de participation citoyenne. Ce nom doit être unique, signficatif, impactant."
            ).strip(".")
            start_date = datetime.now() + timedelta(days=random.randint(-10, 10))
            end_date = start_date + timedelta(hours=random.randint(1, 4))

            meeting = Meeting.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date,
                location=location,
            )
            meetings.append(meeting)

        # Create Proposals
        proposals = []
        proposal_states = ["draft", "published", "closed", "withdrawn"]
        for i in range(100):
            ps = random.choice(participatory_spaces)
            description = self.generate_text(
                f"Génère une courte description pour une proposition dans le cadre de '{ps.name}', qui parle de '{ps.description}'. Ne pas inclure le titre. Une proposition provient d'un citoyen. Cette proposition doit être une demande concrète qui, sur ce sujet, pourrait changer la vie des citoyens."
            )
            title = self.generate_text(
                f"Génère un titre pour la proposition '{description}' dans le cadre de '{ps.name}'. Ce titre doit être unique, signficatif, impactant."
            )

            author_type = random.choice(["person", "organization", "meeting"])
            author_person = None
            author_organization = None
            author_meeting = None

            if author_type == "person":
                author_person = random.choice(persons)
            elif author_type == "organization":
                author_organization = random.choice(organizations)
            else:
                author_meeting = random.choice(meetings)

            start_date = datetime.now() + timedelta(days=random.randint(-20, 20))
            end_date = start_date + timedelta(days=random.randint(7, 30))

            proposal = Proposal.objects.create(
                has_container=ps,
                title=title,
                description=description,
                content=description,
                banner=f"https://placehold.in/{random.randint(200, 400)}x{random.randint(100, 200)}",
                participant_count=random.randint(0, 100),
                vote_count=random.randint(0, 50),
                language="fr",
                proposal_state=random.choice(proposal_states),
                start_date=start_date,
                end_date=end_date,
                author_person=author_person,
                author_organization=author_organization,
                author_meeting=author_meeting,
            )
            proposals.append(proposal)

        # Create Comments
        comments = []
        for i in range(200):
            proposal = random.choice(proposals)
            content = self.generate_text(
                f"Génère un commentaire en relation avec la proposition '{proposal.title}' - '{proposal.description}'."
            )
            creator = random.choice(persons)

            comment = Comment.objects.create(
                content=content, creator=creator, comment_on=proposal
            )
            comments.append(comment)

        # Make some comments replies
        for comment in random.sample(comments, len(comments) // 3):
            choices = [
                c
                for c in comments
                if c.comment_on == comment.comment_on
                and c != comment
                and not c.reply_of
            ]
            if len(choices) > 1:
                reply_to = random.choice(choices)
                comment.reply_of = reply_to
                comment.save()

        self.stdout.write(self.style.SUCCESS("Mock data created successfully!"))
