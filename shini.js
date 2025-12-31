import { safeGet } from "../helpers/http_client.js";
import { detectUpdateDay } from "../helpers/date_utils.js";

// ==========================
// GET MANGA LIST
// ==========================
export async function shinigami(page = 1) {
  try {
    const resp = await safeGet(
      `https://api.shngm.io/v1/manga/list?page=${page}&page_size=30&is_update=true&sort=latest&sort_order=desc`
    );

    if (!resp) return [];

    const data = resp.data?.data ?? [];
    const results = [];

    for (const item of data) {
      if (item.title.includes("Shinigami")) continue;

      const genres = (item.taxonomy?.Genre || []).map((g) => g.slug);
      const author = (item.taxonomy?.Author || [])
        .map((a) => a.name)
        .join(",");

      const chapters = await detailChapter(item.manga_id);
      const chaptersTime = chapters.map((c) => c.chapter_update_at);
      const mostDay = detectUpdateDay(chaptersTime);

      results.push({
        komik_id: item.manga_id,
        title: item.title,
        alternative_title: item.alternative_title,
        release_year: item.release_year,
        release_day: mostDay,
        status:
          item.status === 1
            ? "ongoing"
            : item.status === 2
            ? "completed"
            : "hiatus",
        cover: item.cover_image_url.replace(
          "low/unsafe/filters:format(webp):quality(70)/",
          ""
        ),
        type:
          item.country_id === "KR"
            ? "manhwa"
            : item.country_id === "CN"
            ? "manhua"
            : "manga",
        country: item.country_id,
        rating: item.user_rate,
        readers: item.view_count,
        bookmark: item.bookmark_count,
        genres,
        author,
        description: item.description,
        chapters,
        created_at: item.created_at,
        updated_at: item.updated_at,
      });
    }

    return results;
  } catch (err) {
    console.log("shinigami error:", err);
    return [];
  }
}

// ==========================
// DETAIL CHAPTER
// ==========================
async function detailChapter(komik_id) {
  try {
    const resp = await safeGet(
      `https://api.shngm.io/v1/chapter/${komik_id}/list?page=1&page_size=9999&sort_by=chapter_number&sort_order=desc`
    );

    const data = resp.data?.data ?? [];

    const extractTasks = data.map((item) =>
      extractChapterImages(item.chapter_id)
    );

    const images = await Promise.all(extractTasks);

    const chapters = [];

    for (let i = 0; i < data.length; i++) {
      const chapter = data[i];
      const imgs = images[i];

      if (!imgs) continue;

      chapters.push({
        komik_id,
        chapter_id: chapter.chapter_id,
        chapter_number: chapter.chapter_number,
        chapter_readers: chapter.view_count,
        chapter_images: imgs,
        chapter_update_at: chapter.release_date,
      });
    }

    return chapters;
  } catch (err) {
    console.log("detailChapter error:", err);
    return [];
  }
}

// ==========================
// EXTRACT CHAPTER IMAGES
// ==========================
async function extractChapterImages(chapter_id) {
  try {
    const resp = await safeGet(
      `https://api.shngm.io/v1/chapter/detail/${chapter_id}`
    );

    const data = resp.data?.data;
    if (!data) return [];

    const basePath = data.base_url + data.chapter.path;
    return data.chapter.data.map((img) => basePath + img);
  } catch (err) {
    console.log("extractChapterImages error:", err);
    return [];
  }
}