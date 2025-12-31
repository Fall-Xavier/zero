import fuzz from "fuzzball";
import { supabase } from "./supabaseClient.js";
import { shinigami } from "./providers/shinigami.js";
import { normalize } from "./utils/normalize.js";

// ============================
// MAIN FUNCTION
// ============================
export async function getFromProviders(page = 1) {
  const providers = [shinigami];

  let inserted = 0,
    updated = 0,
    error = 0;

  for (const provider of providers) {
    const resp = await provider(page);

    if (!resp) {
      console.log(`provider ${provider.name} not return list`);
      continue;
    }

    const supaList = await supabase.from("zerokomik").select("*");
    const dataSupabase = supaList.data || [];

    for (const item of resp) {
      const status = await mergeKomik(item, dataSupabase);

      if (status === "inserted") inserted++;
      else if (status === "updated") updated++;
      else error++;
    }
  }

  return { inserted, updated, error };
}

// ============================
// MERGE KOMIK
// ============================
async function mergeKomik(komik, supa) {
  for (const item of supa) {
    const ratio = fuzz.token_set_ratio(
      normalize(komik.title),
      normalize(item.title)
    );

    if (ratio > 80) {
      console.log(`komik already exists : ${komik.title}`);
      await saveChapters(item.komik_id, komik.chapters);
      return "updated";
    }
  }

  console.log(`add komik : ${komik.title}`);

  const copyKomik = { ...komik };
  delete copyKomik.chapters;

  if (!komik.created_at || komik.created_at === "") {
    delete copyKomik.created_at;
  }

  await supabase.from("zerokomik").insert(copyKomik);

  await saveChapters(komik.komik_id, komik.chapters);

  return "inserted";
}

// ============================
// SAVE CHAPTERS
// ============================
async function saveChapters(komik_id, chapters) {
  let inserted = 0;

  try {
    // Cek apakah komik ada
    const checkId = await supabase
      .from("zerokomik")
      .select("komik_id")
      .eq("komik_id", komik_id);

    if (!checkId.data || checkId.data.length === 0) {
      console.log(`skip ${komik_id}: komik_id not found in zerokomik table`);
      return 0;
    }

    // Ambil chapter existing
    const existingChapters = await supabase
      .from("zerochapters")
      .select("chapter_number")
      .eq("komik_id", komik_id);

    const existingNumbers = new Set(
      (existingChapters.data || []).map((c) => String(c.chapter_number).trim())
    );

    // Cari chapter baru
    const newChapters = [];

    for (const chapter of chapters) {
      const chapterNum = String(chapter.chapter_number || "").trim();

      if (!existingNumbers.has(chapterNum)) {
        newChapters.push({
          ...chapter,
          komik_id,
          chapter_number: chapterNum,
        });
      }
    }

    // Insert jika ada chapter baru
    if (newChapters.length > 0) {
      const insertRes = await supabase
        .from("zerochapters")
        .insert(newChapters);

      if (insertRes.error) {
        console.log(
          `failed to insert chapter ${komik_id}: ${insertRes.error.message}`
        );
      } else {
        inserted = newChapters.length;
        console.log(`${komik_id}: ${inserted} new chapter saved`);
      }
    } else {
      console.log(`${komik_id}: all chapters are available`);
    }
  } catch (err) {
    console.log(`failed to save chapter ${komik_id}: ${err}`);
  }

  return inserted;
}