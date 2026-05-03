from django.core.management.base import BaseCommand
from apps.jobs.models import Company

class Command(BaseCommand):
    help = 'Seeds massive, LinkedIn-style authentic company profiles for curated employers.'

    def handle(self, *args, **options):
        profiles = {
            "Hays": """
                <h3>Company Overview</h3>
                <p>Hays plc is the world's leading specialist in recruitment and workforce solutions. With over 50 years of experience, we operate across 33 countries with a team of over 13,000 people. We are experts in placing professionals into permanent, temporary, and interim roles across 20 different specialisms, from Technology and Finance to Construction and Healthcare.</p>
                
                <h3>Workplace Culture</h3>
                <p>At Hays, we believe that the right job can transform a person's life and the right person can transform a business. Our culture is high-performance, fast-paced, and collaborative. We value meritocracy and reward hard work and ambition. You'll find an environment that is supportive yet competitive, where everyone is driven to be the best in their field.</p>
                
                <h3>Career Progression</h3>
                <p>We are deeply committed to the growth of our employees. New joiners undergo intensive training through our Hays 'International Training' program. We provide clear career pathways, whether you want to specialize in a specific niche or move into leadership. Many of our senior directors started their careers at Hays as trainee consultants, proving that there are no limits to how far you can go.</p>
                
                <h3>Core Values</h3>
                <p>Our values define who we are and how we work: <strong>Passionate About People</strong>, <strong>Ambitious</strong>, <strong>Expert</strong>, and <strong>Inquisitive</strong>. We strive to provide excellent service to our clients and candidates while maintaining the highest standards of integrity and professionalism.</p>
            """,

            "Bupa": """
                <h3>Company Overview</h3>
                <p>Bupa is a global healthcare company, founded in 1947 with the purpose of helping people live longer, healthier, happier lives and making a better world. We serve over 38 million customers worldwide through our health insurance, clinics, dental centers, hospitals, and care homes. Unlike many other companies, we have no shareholders, which means we reinvest our profits back into our healthcare services.</p>
                
                <h3>Workplace Culture</h3>
                <p>Working at Bupa is about more than just a job; it's about making a difference. Our culture is inclusive, caring, and purpose-driven. We foster an environment where everyone feels they belong and is empowered to do their best work. We emphasize mental health, well-being, and work-life balance for all our employees.</p>
                
                <h3>Career Progression</h3>
                <p>We offer diverse career opportunities across clinical, corporate, and operational roles. We invest heavily in professional development, offering specialized clinical training, leadership programs, and apprenticeships. Whether you're a nurse, a data analyst, or a customer service representative, we provide the tools and support you need to advance your career.</p>
                
                <h3>Core Values</h3>
                <p>Our values are at the heart of everything we do: <strong>Brave</strong>, <strong>Caring</strong>, and <strong>Responsible</strong>. These values guide our interactions with customers and colleagues alike, ensuring that we always act with compassion and accountability.</p>
            """,

            "Tesco": """
                <h3>Company Overview</h3>
                <p>Tesco is a leading multinational retailer and the largest supermarket chain in the UK. Since 1919, we have grown from a single market stall to a global brand serving millions of customers every week. Our operations span thousands of stores, an industry-leading online grocery business, and a range of financial and mobile services.</p>
                
                <h3>Workplace Culture</h3>
                <p>Our culture is built on the principle of 'Every Little Helps.' We are a diverse and inclusive team where everyone is welcome. We believe in working together to provide the best service for our customers and communities. The environment is friendly, collaborative, and fast-moving, reflecting the dynamic nature of retail.</p>
                
                <h3>Career Progression</h3>
                <p>As one of the UK's largest employers, we offer unparalleled career variety. We have robust graduate programs, management training schemes, and internal development pathways for store colleagues. We encourage our people to gain experience across different departments, from logistics and marketing to technology and finance.</p>
                
                <h3>Core Values</h3>
                <p>Our values guide us in everything we do: <strong>No one tries harder for customers</strong>, <strong>We treat people how they want to be treated</strong>, and <strong>Every little help makes a big difference</strong>. These values help us build trust and loyalty with our customers and colleagues.</p>
            """,

            "Deliveroo": """
                <h3>Company Overview</h3>
                <p>Deliveroo is on a mission to be the definitive food company. Founded in London in 2013, we have revolutionized the way people eat by connecting them with their favorite restaurants and grocery stores. We operate in multiple markets globally, powered by our world-class technology and a network of thousands of riders and partners.</p>
                
                <h3>Workplace Culture</h3>
                <p>Deliveroo is a fast-paced, innovative tech company. We value ownership, agility, and a 'get stuff done' attitude. Our culture is highly collaborative, with cross-functional teams working together to solve complex logistical and technical challenges. We embrace diversity and encourage different perspectives to drive innovation.</p>
                
                <h3>Career Progression</h3>
                <p>We are a high-growth company where you can have a massive impact from day one. We offer opportunities for rapid career advancement for those who are ambitious and results-oriented. We provide mentorship, learning stipends, and the chance to work on cutting-edge projects that define the future of food delivery.</p>
                
                <h3>Core Values</h3>
                <p>We are guided by our 'Operating Principles': <strong>Customer First</strong>, <strong>Ownership</strong>, <strong>High Standards</strong>, <strong>Agility</strong>, and <strong>Intellectual Honesty</strong>. These principles help us maintain our competitive edge and deliver an exceptional experience for our users.</p>
            """,

            "Barclays": """
                <h3>Company Overview</h3>
                <p>Barclays is a British universal bank with a history dating back over 330 years. We support consumers and small businesses through our retail banking services, and large corporations and institutions through our world-class investment bank. Our purpose is to deploy finance responsibly to support people and businesses, acting with empathy and integrity.</p>
                
                <h3>Workplace Culture</h3>
                <p>Our culture is founded on excellence and a commitment to doing the right thing. We value diverse perspectives and are dedicated to creating an inclusive environment where everyone can thrive. We place a strong emphasis on professional ethics, innovation, and community engagement.</p>
                
                <h3>Career Progression</h3>
                <p>We offer extensive career opportunities across a wide range of functions, including Technology, Finance, Risk, and Operations. Our graduate and internship programs are among the most respected in the industry. We provide continuous learning opportunities, including professional qualifications and leadership development modules.</p>
                
                <h3>Core Values</h3>
                <p>Our values define the way we operate: <strong>Respect</strong>, <strong>Integrity</strong>, <strong>Service</strong>, <strong>Excellence</strong>, and <strong>Stewardship</strong>. These values are the bedrock of our business and guide how we interact with our customers, clients, and each other.</p>
            """,

            "Vodafone": """
                <h3>Company Overview</h3>
                <p>Vodafone is a leading global telecommunications company, providing mobile and fixed-line services, broadband, and digital solutions to millions of people and businesses. We are pioneers in connectivity, from launching the first cellular network in the UK to leading the way in 5G and Internet of Things (IoT) technologies.</p>
                
                <h3>Workplace Culture</h3>
                <p>Our culture is digital-first, agile, and inclusive. We believe in the power of technology to connect people and improve lives. We foster an environment of experiment-led learning, where employees are encouraged to take risks and innovate. We champion flexible working and prioritize the well-being of our global workforce.</p>
                
                <h3>Career Progression</h3>
                <p>We offer a world of opportunity across tech, commercial, and corporate functions. Our 'Discover' graduate program and apprenticeship schemes provide a fantastic foundation for a career in tech. We support internal mobility and provide extensive digital learning resources to help you stay ahead in an ever-evolving industry.</p>
                
                <h3>Core Values</h3>
                <p>Our purpose is to connect for a better future, and our values reflect this: <strong>Speed</strong>, <strong>Simplicity</strong>, and <strong>Trust</strong>. We are committed to operating in a way that is ethical and sustainable, creating a positive impact on the planet.</p>
            """,

            "Sky": """
                <h3>Company Overview</h3>
                <p>Sky is Europe's leading media and entertainment company and is proud to be part of the Comcast group. We entertain millions of customers through our premium content, award-winning news, and exclusive sports coverage. Beyond TV, we are a major provider of broadband and mobile services across several European markets.</p>
                
                <h3>Workplace Culture</h3>
                <p>Sky is a vibrant, creative, and inclusive place to work. We believe in being 'Better Together' and value the unique contributions of every individual. Our environment is fast-paced and collaborative, with a strong emphasis on innovation and storytelling. We are committed to being a force for good in the communities we serve.</p>
                
                <h3>Career Progression</h3>
                <p>We offer a wide range of early-career opportunities, from content production and journalism to software engineering and data science. Our development programs are designed to help you build your skills and grow your career. We encourage lateral moves and provide the mentorship and support needed to succeed in a diverse media landscape.</p>
                
                <h3>Core Values</h3>
                <p>Our values are at the heart of our brand: <strong>Forward-looking</strong>, <strong>Creative</strong>, <strong>Customer-led</strong>, and <strong>Collaborative</strong>. We strive to push boundaries and deliver an exceptional entertainment experience for our viewers.</p>
            """,

            "Sainsbury": """
                <h3>Company Overview</h3>
                <p>Sainsbury's is a leading multi-brand, multi-channel retailer, comprising Sainsbury's supermarkets, Argos, Habitat, and Sainsbury's Bank. Since 1869, we have been dedicated to providing our customers with high-quality products at great value. Our purpose is that 'driven by our passion for food, together we serve and help every customer'.</p>
                
                <h3>Workplace Culture</h3>
                <p>Our culture is warm, welcoming, and community-focused. We are a place where you can be yourself and do your best work. We value teamwork and are committed to creating an inclusive environment where everyone feels respected. We take our social and environmental responsibilities seriously, working to make a positive impact on society.</p>
                
                <h3>Career Progression</h3>
                <p>We offer a vast array of career paths across retail, logistics, marketing, and digital. We have comprehensive development programs for colleagues at all levels, including leadership training and specialist skill workshops. We believe in promoting from within and providing the support needed for long-term career growth.</p>
                
                <h3>Core Values</h3>
                <p>Our values guide our decision-making: <strong>Be your best</strong>, <strong>Keep it simple</strong>, <strong>Do the right thing</strong>, and <strong>Love our customers</strong>. These values help us build lasting relationships with our customers and colleagues.</p>
            """,

            "O2": """
                <h3>Company Overview</h3>
                <p>O2 is the commercial brand of Virgin Media O2, a leading telecommunications provider in the UK. We provide millions of people with mobile connectivity, broadband, and digital services. We are known for our customer-centric approach, award-winning network, and iconic brand presence, including The O2 arena.</p>
                
                <h3>Workplace Culture</h3>
                <p>Our culture is energetic, customer-obsessed, and digital-first. We believe in 'Supercharging the UK' and are passionate about the power of connectivity. We foster a collaborative and flexible environment where everyone is encouraged to bring their whole self to work. We value bold ideas and a proactive approach to problem-solving.</p>
                
                <h3>Career Progression</h3>
                <p>We offer a range of career opportunities across technology, sales, marketing, and customer experience. Our early-careers programs provide a great start for graduates and apprentices. We offer extensive learning and development resources, supporting you to build the skills needed for a successful career in the digital sector.</p>
                
                <h3>Core Values</h3>
                <p>Our values reflect our commitment to our customers and each other: <strong>Bold</strong>, <strong>Open</strong>, and <strong>Trusted</strong>. We strive to be a brand that people can rely on, delivering an exceptional experience every time.</p>
            """,

            "EE": """
                <h3>Company Overview</h3>
                <p>EE, part of the BT Group, is the UK's largest and most advanced mobile network operator. We were the first to launch 4G and 5G in the UK, and we continue to lead the way in network technology and customer service. We provide mobile, broadband, and home security services to millions of personal and business customers.</p>
                
                <h3>Workplace Culture</h3>
                <p>EE is a fast-moving, tech-driven, and inclusive company. We are part of the BT Group, meaning we have the agility of a leading mobile brand backed by the resources of a global communications provider. Our culture is collaborative and performance-oriented, with a strong focus on technical excellence and customer satisfaction.</p>
                
                <h3>Career Progression</h3>
                <p>We offer a world of opportunity across technology, commercial, and operational functions. Our graduate and apprentice programs are highly regarded, providing hands-on experience and professional development. we support career growth through internal mobility, mentorship, and extensive training resources.</p>
                
                <h3>Core Values</h3>
                <p>Our values define how we work together and serve our customers: <strong>Personal</strong>, <strong>Simple</strong>, and <strong>Brilliant</strong>. We are committed to making a positive difference through the power of connectivity.</p>
            """
        }

        generic_profile = """
            <h3>Company Overview</h3>
            <p>This organization is a verified hiring partner currently sourcing top-tier talent through the broader employment network. As a dynamic and forward-thinking enterprise, the company operates within a highly competitive sector, prioritizing strategic growth, operational excellence, and the continuous acquisition of skilled professionals to drive their corporate objectives forward.</p>
            
            <h3>Workplace Culture</h3>
            <p>The organization places a significant emphasis on cultivating a diverse, inclusive, and high-performance workplace culture. They actively seek out individuals who possess a strong work ethic, a proactive problem-solving mindset, and the agility to thrive in a fast-paced environment. The leadership team is dedicated to providing employees with a supportive and collaborative work environment.</p>
            
            <h3>Career Progression</h3>
            <p>The company offers a comprehensive onboarding process designed to integrate new team members smoothly into their operational ecosystem. Employees can expect to work on impactful projects that directly influence the company's success. For ambitious professionals looking to join a growth-oriented organization, this company presents a compelling opportunity to build a rewarding career trajectory.</p>
            
            <h3>Core Values</h3>
            <p>The organization's values are built upon a foundation of efficiency, client satisfaction, and the delivery of high-quality products or services. They are committed to maintaining a robust market presence by continuously adapting to evolving industry trends and consumer demands.</p>
        """

        companies = Company.objects.all()
        updated_count = 0

        for company in companies:
            matched = False
            for target, desc in profiles.items():
                if target.lower() in company.name.lower():
                    company.description = desc
                    company.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated specific profile for: {company.name}"))
                    updated_count += 1
                    matched = True
                    break
            
            if not matched:
                if not company.description or "hiring entry-level talent" in company.description.lower():
                    company.description = generic_profile
                    company.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated generic profile for: {company.name}"))
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {updated_count} robust company profiles into the database!"))
