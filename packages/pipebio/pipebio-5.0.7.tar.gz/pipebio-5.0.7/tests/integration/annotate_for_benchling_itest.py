import uuid
import os
import re
from pipebio.pipebio_client import PipebioClient
from pipebio.models.job_type import JobType
from pipebio.annotate.AnnotateForBenchlingParams import (
    AnnotateForBenchlingParams,
    GermlineBasedDomain,
    LinkerDomain,
    ConstantDomain,
    ShortScaffold,
)
from pipebio.shared_python.selection_range import SelectionRange
from tests.test_helpers import get_project_id

class TestAnnotateForBenchlingIntegration:

    def setup_method(self):
        self.api_url = os.environ.get("PIPE_API_URL")
        print('PIPE_API_URL', self.api_url)

    def test_full_sdk_run(self):

        print('Starting')

        client = PipebioClient(url=self.api_url)

        project_id = get_project_id(client)
        organization_id = client.user['org']['id']

        # Currently it is not possible to get the germlines directly from the SDK,
        # so instead we do the following hack.

        # Get the germline ID.
        response = client.session.get(f'/api/v2/organizations/{organization_id}/lists')
        germlines = [obj for obj in response.json()['data'] if obj['kind'] == 'germline']

        # Filter for human IMGT germlines
        human_imgt_germlines = [
            g for g in germlines
            if 'human' in g['name'].lower() and 'imgt' in g['name'].lower() and 'tcr' not in g['name'].lower()
        ]

        # Extract version numbers if present
        def get_version(name):
            match = re.search(r'v?(\d+(?:\.\d+)*)', name)
            return float(match.group(1)) if match else -1

        # Sort by version (highest first)
        human_imgt_germlines.sort(key=lambda g: get_version(g['name']), reverse=True)

        human_germline = human_imgt_germlines[0] if human_imgt_germlines else None
        if not human_germline:
            raise Exception('No human IMGT germline found')

        germline_id = human_germline['id']
        print(f"Using germline: {human_germline['name']} (ID: {germline_id})")

        job_run = f'test-{uuid.uuid4()}'

        folder = client.entities.create_folder(
            project_id=project_id,
            name=job_run,
            parent_id=None,
            visible=True
        )

        folder_id = folder['id']

        print('Uploading query/reference sequences in parallel.')
        test_data_dir = os.path.join(os.path.dirname(__file__), '..', 'sample_data')
        uploads = [
            client.upload_file(
                file_name='aa_database.fasta',
                absolute_file_location=os.path.join(test_data_dir, 'aa_database.fasta'),
                parent_id=folder_id,
                project_id=project_id
            ),
            client.upload_file(
                file_name='test_sequences_aa.fasta',
                absolute_file_location=os.path.join(test_data_dir, 'test_sequences_aa.fasta'),
                parent_id=folder_id,
                project_id=project_id
            )
        ]

        # Wait for uploads to complete.
        job_ids = list(job['id'] for job in uploads)
        # TODO Confirm if these are in order.
        upload_jobs = client.jobs.poll_jobs(job_ids)
        reference_db_doc_id = upload_jobs[0]['outputEntities'][0]['id']
        query_db_doc_id = upload_jobs[1]['outputEntities'][0]['id']


        params = AnnotateForBenchlingParams(
            target_folder_id=folder_id,
            scaffolds=[
                ShortScaffold(
                    selection=SelectionRange(start_id=1, end_id=2),
                    domains=[
                        GermlineBasedDomain(name='vh', germline_ids=[germline_id])
                    ]
                ),
                ShortScaffold(
                    selection=SelectionRange(start_id=3, end_id=4),
                    domains=[
                        GermlineBasedDomain(name='vh', germline_ids=[germline_id]),
                        LinkerDomain(name='l', reference_sequences=[reference_db_doc_id]),
                        GermlineBasedDomain(name='vl', germline_ids=[germline_id])
                    ]
                ),
                ShortScaffold(
                    selection=SelectionRange(start_id=5, end_id=6),
                    domains=[
                        GermlineBasedDomain(name='vl', germline_ids=[germline_id]),
                        LinkerDomain(name='l1', reference_sequences=[reference_db_doc_id]),
                        GermlineBasedDomain(name='vh', germline_ids=[germline_id]),
                        LinkerDomain(name='l2', reference_sequences=[reference_db_doc_id]),
                        GermlineBasedDomain(name='vh', germline_ids=[germline_id]),
                        ConstantDomain(name='ch1', reference_sequences=[reference_db_doc_id]),
                        ConstantDomain(name='hinge', reference_sequences=[reference_db_doc_id]),
                        ConstantDomain(name='ch2', reference_sequences=[reference_db_doc_id]),
                        ConstantDomain(name='ch3', reference_sequences=[reference_db_doc_id]),
                        LinkerDomain(name='l3', reference_sequences=[reference_db_doc_id]),
                        GermlineBasedDomain(name='vh', germline_ids=[germline_id])
                    ]
                ),
                ShortScaffold(
                    selection=SelectionRange(start_id=7, end_id=8),
                    domains=[
                        GermlineBasedDomain(name='vl', germline_ids=[germline_id]),
                        LinkerDomain(name='l1', reference_sequences=[reference_db_doc_id]),
                        GermlineBasedDomain(name='vh', germline_ids=[germline_id]),
                        LinkerDomain(name='l2', reference_sequences=[reference_db_doc_id]),
                        GermlineBasedDomain(name='vh', germline_ids=[germline_id]),
                        ConstantDomain(name='ch1', reference_sequences=[reference_db_doc_id]),
                        ConstantDomain(name='hinge', reference_sequences=[reference_db_doc_id]),
                        ConstantDomain(name='ch2', reference_sequences=[reference_db_doc_id]),
                        ConstantDomain(name='ch3', reference_sequences=[reference_db_doc_id]),
                        LinkerDomain(name='l3', reference_sequences=[reference_db_doc_id]),
                        GermlineBasedDomain(name='vh', germline_ids=[germline_id]),
                        LinkerDomain(name='l4', reference_sequences=[reference_db_doc_id]),
                        GermlineBasedDomain(name='vl', germline_ids=[germline_id])
                    ]
                ),
            ]
        )

        annotation_job_id = client.jobs.create(
            shareable_id=project_id,
            job_type=JobType.AnnotateForBenchlingJob,
            name=job_run,
            input_entity_ids=[reference_db_doc_id, query_db_doc_id],
            params=params.to_json(),
            owner_id=organization_id,
        )
        # Set a timeout to allow sufficient time for the job to finish.
        client.jobs.poll_job(job_id=annotation_job_id, timeout_seconds=60*10)
        annotation_job = client.jobs.get(annotation_job_id)

        if not annotation_job.get('outputEntities'):
            raise Exception(f"Job failed or produced no output. Status: {annotation_job.get('status')}")

        result_id = annotation_job['outputEntities'][0]['id']

        # Download the results (e.g. for post-processing in Benchling).
        absolute_location = os.path.join(os.getcwd(), f'Benchling annotation - {job_run}.tsv')
        client.sequences.download(result_id, destination=absolute_location)
        print(f'Downloaded results to: {absolute_location}')


