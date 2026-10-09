import json
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

ASSISTANT = Path(__file__).resolve().parents[2] / 'car mechanic assistant'
sys.path.insert(0, str(ASSISTANT))
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStore
from src.rag_system import MechanicAssistant
from src.evaluate_retrieval import evaluate

class Embeddings:
    model = 'audit-fixture-embedding'
    dimensions = 3
    def embed_query(self, query):
        return [1., 0., 0.]
    def embed_batch(self, texts, **kwargs):
        return [[1., 0., 0.] for _ in texts]

def index(tmp_path, rows):
    kb = tmp_path / 'kb'
    kb.mkdir()
    for name, tags, text in rows:
        (kb / (name + '.md')).write_text(text + '\n```json\n' + json.dumps(tags) + '\n```')
    store = VectorStore(tmp_path / 'index', embeddings=Embeddings())
    store.add_documents(DocumentProcessor().process_knowledge_base(kb))
    return store

def test_contradictory_generic_applicability_rejected():
    for metadata in ({'scope': 'generic', 'make': 'BMW'}, {'scope': 'generic', 'year_range': '2007-2011'}):
        with pytest.raises(ValueError, match='generic'):
            DocumentProcessor()._sanitize_metadata(metadata)

def test_public_reference_library_is_separate_and_attributed():
    processor = DocumentProcessor()
    chunks = processor.process_knowledge_base(ASSISTANT / 'public_reference_corpus')
    assert len(chunks) == 12
    assert {chunk.metadata['language'] for chunk in chunks} == {'en', 'zh', 'ja'}
    assert processor.manifest['accepted_unique_pdf_pages'] == 0
    assert len({chunk.metadata['source_url'] for chunk in chunks}) == 4
    for chunk in chunks:
        assert chunk.metadata['scope'] == 'generic'
        assert chunk.metadata['corpus_kind'] == 'public_reference_placeholder'
        assert chunk.metadata['review_status'] == 'summary_checked_not_repair_verified'
        assert chunk.metadata['source_url'].startswith('https://')
        assert 'Placeholder only:' in chunk.content

def test_missing_vehicle_details_do_not_admit_specific_instructions(tmp_path):
    store = index(tmp_path, [('specific', {'make': 'BMW', 'engine': 'N54'}, 'N54 procedure'),
                             ('generic', {'scope': 'generic'}, 'General checks'),
                             ('unknown', {}, 'Unverified instructions')])
    for vehicle in (None, {'make': 'BMW'}):
        files = {r['metadata']['filename'] for r in store.query_with_reranking('checks', vehicle_info=vehicle)}
        assert files == {'generic.md'}

def test_engine_options_and_engine_only_manual(tmp_path):
    store = index(tmp_path, [('honda', {'make': 'Honda', 'engine': 'K20_K24'}, 'VTC checks'),
                             ('bmw', {'make': 'BMW', 'engine': 'N52B30'}, 'Spark plug torque')])
    result = store.query_with_reranking('VTC', vehicle_info={'make': 'Honda', 'engine': 'k20'})
    assert [r['metadata']['filename'] for r in result] == ['honda.md']
    result = store.query_with_reranking('torque', vehicle_info={'make': 'BMW', 'model': 'E90', 'engine': 'N52B30'})
    assert [r['metadata']['filename'] for r in result] == ['bmw.md']
    assert not store.query_with_reranking('torque', vehicle_info={'make': 'BMW', 'engine': 'N54'})

def test_low_similarity_abstains_and_scores_are_inspectable(tmp_path):
    store = index(tmp_path, [('generic', {'scope': 'generic'}, 'Misfire checks')])
    result = store.query_with_reranking('misfire')[0]
    assert sum(result['score_components'].values()) == pytest.approx(result['relevance_score'])
    store.embeddings.embed_query = lambda query: [0., 1., 0.]
    assert store.query_with_reranking('unrelated') == []

def test_sidecar_changes_have_distinct_provenance(tmp_path):
    path = tmp_path / 'manual.md'
    path.write_text('Repair procedure')
    sidecar = path.with_suffix('.md.metadata.json')
    sidecar.write_text('{"make":"BMW"}')
    first = DocumentProcessor()
    first.process_document(path)
    sidecar.write_text('{"make":"Honda"}')
    second = DocumentProcessor()
    second.process_document(path)
    assert first.manifest != second.manifest

def test_collection_metadata_must_match_release(tmp_path):
    store = VectorStore(tmp_path / 'index', embeddings=Embeddings())
    store.collection.modify(metadata={'schema': -1})
    with pytest.raises(ValueError, match='collection'):
        VectorStore(tmp_path / 'index', embeddings=Embeddings())

@pytest.mark.parametrize('field', ['relevant_ids', 'retrieved_ids'])
def test_evaluator_rejects_strings_instead_of_id_lists(field):
    label = {'query_id': 'q', 'category': 'misfire_ignition', 'language': 'en', 'reviewer': 'fixture',
             'reviewed_at': '2026-10-09', 'relevant_ids': ['abc']}
    with pytest.raises(ValueError, match='date'):
        evaluate([{**label, 'reviewed_at': '20261009'}], [])
    run = {'query_id': 'q', 'retrieved_ids': ['abc']}
    (label if field == 'relevant_ids' else run)[field] = 'abc'
    with pytest.raises(ValueError):
        evaluate([label], [run])

def test_generation_requires_known_citations_and_no_sources_skip_model():
    assistant = MechanicAssistant.__new__(MechanicAssistant)
    assistant.model_name = 'test'
    assistant.vector_store = SimpleNamespace(embeddings=Embeddings(), identity={'schema': 3},
                                             get_workshop_rules=lambda: 'Policy')
    passage = {'id': 'known', 'content': 'Check voltage', 'metadata': {'filename': 'manual.md', 'location': 'page 1'}}
    assistant.retrieve_context = lambda *args, **kwargs: [passage]
    for text in ('Check voltage', 'Check voltage [source:invented]'):
        assistant.generate_response = lambda *args, answer=text: answer
        with pytest.raises(ValueError, match='citation'):
            assistant.query('question')
    assistant.generate_response = lambda *args: 'Check voltage [source:known]'
    assert assistant.query('question')['metadata']['cited_source_ids'] == ['known']
    assistant.retrieve_context = lambda *args, **kwargs: []
    assistant.generate_response = lambda *args: pytest.fail('No evidence must skip model generation')
    assert assistant.query('unknown')['num_sources'] == 0
    from PIL import Image
    import io
    buffer = io.BytesIO()
    Image.new('RGB', (2, 2)).save(buffer, format='PNG')
    assistant.generate_response_with_image = lambda *args: pytest.fail('No repair evidence must skip generation')
    assert assistant.query_with_image('unknown', buffer.getvalue())['num_sources'] == 0


def test_policy_snapshot_checksum_and_collection_name(tmp_path):
    import hashlib
    root = tmp_path / 'index'
    store = VectorStore(root, embeddings=Embeddings())
    policy = 'Versioned policy'
    (root / 'policy.md').write_text(policy)
    identity = {**store.identity, 'policy_hash': hashlib.sha256(policy.encode()).hexdigest(), 'collection': store.collection_name}
    (root / 'release.json').write_text(json.dumps(identity))
    loaded = VectorStore(root, embeddings=Embeddings())
    assert loaded.get_workshop_rules() == policy
    assert loaded.identity['policy_hash'] == identity['policy_hash']
    with pytest.raises(ValueError, match='collection name'):
        VectorStore(root, embeddings=Embeddings(), collection_name='wrong-name')
    (root / 'policy.md').write_text('Tampered')
    with pytest.raises(ValueError, match='policy checksum'):
        VectorStore(root, embeddings=Embeddings())


def test_feedback_retains_reviewable_question_and_answer(tmp_path):
    import sqlite3
    from web_app import create_app
    class Assistant:
        def query(self, text):
            return {'query': text, 'response': 'Fixture answer', 'sources': [], 'metadata': {'cited_source_ids': []}}
    path = tmp_path / 'feedback.sqlite'
    response = create_app(Assistant(), path).test_client().post('/query', json={'query': 'Fixture question'})
    assert response.status_code == 200
    with sqlite3.connect(path) as db:
        record = json.loads(db.execute('SELECT sources FROM queries').fetchone()[0])
    assert record['query'] == 'Fixture question' and record['response'] == 'Fixture answer'


def test_citation_validation_accepts_whitespace_without_relaxing_id_check():
    assert MechanicAssistant._validate_citations('Check [Source: known]', [{'id': 'known'}]) == ['known']
    with pytest.raises(ValueError, match='citation'):
        MechanicAssistant._validate_citations('Check [Source: invented]', [{'id': 'known'}])


def test_citation_location_format_does_not_hide_unknown_id():
    assert MechanicAssistant._validate_citations('Check [source: known; manual.pdf, page 2]', [{'id': 'known'}]) == ['known']
    with pytest.raises(ValueError, match='citation'):
        MechanicAssistant._validate_citations('Check [source: known; ' + 'a' * 64 + ']', [{'id': 'known'}])
