async def read_scan_result(url: str) -> str: ...


async def highlight_image(url: str) -> str: ...


async def read_text(url: str) -> str: ...


async def read_page(skimmed: str, img_url: str, text: str) -> str: ...


async def debug_a_and_b_images(a: str, b: str) -> str: ...


async def skim_chapter(texts: list[str]) -> str: ...


async def analyze_characters(readings: list[str]) -> dict[str, Any]: ...


async def analyze_page(
    chapter: dict[str, Any],
    characters: dict[str, Any],
    reading: str,
) -> dict[str, Any]: ...


async def analyze_chapter(
    readings: list[str], characters: dict[str, Any]
) -> dict[str, Any]: ...


async def extract_proper_nouns(
    chapter: dict[str, Any],
    page_analyses: list[dict[str, Any]],
) -> list[str]: ...


async def export_results(
    page_analyses: list[dict[str, Any]],
    proper_nouns: list[str],
) -> str: ...


async def read(
    work_id: str,
    page_count: int,
):
    async with Workflow() as w:
        _ = w.run(load_image("a.png"))
        aimgs = [w.run(load_image(f"file_{i}.png")) for i in range(page_count)]
        ahimgs = [aimg.then(highlight_image) for aimg in aimgs]
        atexts = [ahimg.then(read_text) for ahimg in ahimgs]
        skimmed = await w.gather(atexts).then(skim_chapter)
        areadings = [
            (img * text).then(lambda img, text: read_page(skimmed, img, text))
            for img, text in zip(aimgs, atexts)
        ]
        agreadings = w.gather(areadings)
        acharacters = agreadings.then(analyze_characters)
        achapter = (agreadings * acharacters).then(analyze_chapter)
        apage_analyses = [
            (achapter * acharacters * ar).then(analyze_page) for ar in areadings
        ]
        aproper_nouns = (achapter * w.gather(apage_analyses)).then(extract_proper_nouns)
        aresults = (w.gather(apage_analyses) * aproper_nouns).then(export_results)
        return await aresults
