type PageCardProps = {
  title: string;
  description: string;
};

export function PageCard({ title, description }: PageCardProps) {
  return (
    <section>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
  );
}
