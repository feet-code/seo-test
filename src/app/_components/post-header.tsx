import DateFormatter from "./date-formatter";
import { PostTitle } from "@/app/_components/post-title";
import { type Author } from "@/interfaces/author";

type Props = {
  title: string;
  date: string;
  author?: Author;
};

export function PostHeader({ title, date, author }: Props) {
  return (
    <>
      <PostTitle>{title}</PostTitle>
      <div className="max-w-2xl mx-auto">
        <div className="mb-10 text-lg text-neutral-600 dark:text-neutral-300">
          {author?.name ? <span>By {author.name} · </span> : null}
          <DateFormatter dateString={date} />
        </div>
      </div>
    </>
  );
}
