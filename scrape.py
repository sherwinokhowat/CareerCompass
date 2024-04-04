"""
CSC111 Winter 2024 Course Project 2: CareerCompass

This Python module contains the scraping functionality
of our application. This module will scrape GlassDoor
and creates a CSV file which is used as our data set.

Copyright and Usage Information
===============================
This file is provided solely for the personal and private use of the instructors
and teaching assistants of CSC111 at the University of Toronto St. George campus.
All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright of these files,
please contact us through Github using the "contact" button within our application.

This file is Copyright (c) 2024 Sherwin Okhowat, Kush Gandhi, David Cen, Tony Qi.
"""

from __future__ import annotations
from typing import Any
from random import randint
import time
import asyncio
import json
import requests
import aiohttp
from utility import clear_csv, write_csv, sanitize_details

# ====================================================================================
# Scraper
# ====================================================================================


def scrape() -> None:
    """
    Scrapes and stores all available software internships available
    located in Canada and the US on Glassdoor.

    NOTE: Glassdoor API is unstable and occasionally a faulty repsonse will
    be returned which we raise an error for.
    """
    ids = set()
    scrape_us_jobs(ids)
    scrape_ca_jobs(ids)


# ====================================================================================
# Synchronous Scraping Functions
# ====================================================================================


def scrape_us_jobs(ids: set[int]) -> None:
    """
    Scrapes Glassdoor for every software internship job listing in the United States.

    <fetch_jobs_us> with the respective pagination cursor, which returns a dictionary of
    30 job postings and their generalized information. The next pagination cursor is then parsed
    (if there is one), and <process_job_listings> is executed which parses and stores
    relevant details

    NOTE: This function will continue scraping jobs until there are no more pagination cursors
    left (i.e., no more pages of job postings)!
    """
    clear_csv()
    cursor = "AB4AAIEAAAAAAAAAAAAAAAAAAiR3vUAAAwAAAQAA"  # initial us cursor

    page_number = 1
    tries = 0
    while tries < 3:
        found = False
        job_list_data = fetch_jobs_us(cursor)

        paginations = job_list_data["paginationCursors"]
        jobs = job_list_data["jobListings"]  # this is the 30 jobs

        asyncio.run(process_job_listings(jobs, ids))
        time.sleep(0.15)
        for pagination in paginations:  # find the next cursor.
            if (
                pagination["pageNumber"] > page_number
            ):  # The first one should be the next one
                page_number += 1
                cursor = pagination["cursor"]
                found = True
                tries = 0
                break
        if not found:
            tries += 1
            time.sleep(3)


def scrape_ca_jobs(ids: set[int]) -> None:
    """
    Scrapes Glassdoor for every software internship job listing in Canada.

    <fetch_jobs_ca> with the respective pagination cursor, which returns a dictionary of
    30 job postings and their generalized information. The next pagination cursor is then parsed
    (if there is one), and <process_job_listings> is executed which parses and stores
    relevant details

    NOTE: This function will continue scraping jobs until there are no more pagination cursors
    left (i.e., no more pages of job postings)!
    """
    cursor = "AB4AAIEAAAAAAAAAAAAAAAAAAiUV1vYAAwAAAQAA"  # initial ca cursor

    page_number = 1
    tries = 0
    while tries < 3:
        found = False
        job_list_data = fetch_jobs_ca(cursor)

        paginations = job_list_data["paginationCursors"]
        jobs = job_list_data["jobListings"]  # this is the 30 jobs

        asyncio.run(process_job_listings(jobs, ids))
        time.sleep(0.15)
        for pagination in paginations:  # find the next cursor.
            if (
                pagination["pageNumber"] > page_number
            ):  # The first one should be the next one
                page_number += 1
                cursor = pagination["cursor"]
                found = True
                tries = 0
                break
        if not found:
            tries += 1
            time.sleep(3)


# ====================================================================================
# Fetch Functions
# ====================================================================================


def fetch_jobs_us(cursor: str) -> dict[Any] | None:
    """
    Returns a dictionary representing the JSON response for
    30 job postings in the US and their generalized information.

    <cursor> is the pagination cursor for the current query.

    If an HTTP status of >= 300 is retrieved by the POST request,
    the specific HTTP status is printed and None is returned.
    """
    target_url = "https://www.glassdoor.ca/graph"
    headers = {
        "content-type": "application/json",
        "gd-csrf-token": "g1Pap2CLYOr1TlDIB7v_1w:BVvkWc1Czkiaae7GSEeK72VaaOmeSnPiMoU5Fv5z-J6bZkVxUHOBZ6o2lxrOBW362CjJXZ"
        "hj5oHDq2uFnyq8tA:TaaIXLlfr3qKo1E8EYjcg5mMXgl99BTp8s-c4hq1Lp0",
        "User-Agent": "",
    }
    job_list_query = f'[{{"operationName":"uilTrackingMutation","variables":{{"events":[{{"eventType":"JOB_SEEN","jobTrackingKeys":["5-yul1-0-1hpneooe7iqsp800-57ba39f093e850ef"],"jobCountryId":1,"pageType":"SERP"}}]}},"query":"mutation uilTrackingMutation($events: [EventContextInput]!) {{\\n  trackEvents(events: $events) {{\\n    eventType\\n    resultStatus\\n    message\\n    clickId\\n    clickGuid\\n    __typename\\n  }}\\n}}\\n"}},{{"operationName":"JobSearchResultsQuery","variables":{{"excludeJobListingIds":[],"filterParams":[],"keyword":"software internship","locationId":1,"locationType":"COUNTRY","numJobsToShow":30,"originalPageUrl":"https://www.glassdoor.ca/Job/united-states-software-internship-jobs-SRCH_IL.0,13_IN1_KO14,33.htm","parameterUrlInput":"IL.0,13_IN1_KO14,33","pageType":"SERP","queryString":"","seoFriendlyUrlInput":"united-states-software-internship-jobs","seoUrl":true,"pageCursor":"{cursor}","pageNumber":1}},"query":"query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String, $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String, $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean) {{\\n  jobListings(\\n    contextHolder: {{queryString: $queryString, pageTypeEnum: $pageType, searchParams: {{excludeJobListingIds: $excludeJobListingIds, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, filterParams: $filterParams, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR}}}}\\n  ) {{\\n    companyFilterOptions {{\\n      id\\n      shortName\\n      __typename\\n    }}\\n    filterOptions\\n    indeedCtk\\n    jobListings {{\\n      ...JobView\\n      __typename\\n    }}\\n    jobListingSeoLinks {{\\n      linkItems {{\\n        position\\n        url\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    jobSearchTrackingKey\\n    jobsPageSeoData {{\\n      pageMetaDescription\\n      pageTitle\\n      __typename\\n    }}\\n    paginationCursors {{\\n      cursor\\n      pageNumber\\n      __typename\\n    }}\\n    indexablePageForSeo\\n    searchResultsMetadata {{\\n      searchCriteria {{\\n        implicitLocation {{\\n          id\\n          localizedDisplayName\\n          type\\n          __typename\\n        }}\\n        keyword\\n        location {{\\n          id\\n          shortName\\n          localizedShortName\\n          localizedDisplayName\\n          type\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      footerVO {{\\n        countryMenu {{\\n          childNavigationLinks {{\\n            id\\n            link\\n            textKey\\n            __typename\\n          }}\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      helpCenterDomain\\n      helpCenterLocale\\n      jobAlert {{\\n        jobAlertExists\\n        __typename\\n      }}\\n      jobSerpFaq {{\\n        questions {{\\n          answer\\n          question\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      jobSerpJobOutlook {{\\n        occupation\\n        paragraph\\n        heading\\n        __typename\\n      }}\\n      showMachineReadableJobs\\n      __typename\\n    }}\\n    serpSeoLinksVO {{\\n      relatedJobTitlesResults\\n      searchedJobTitle\\n      searchedKeyword\\n      searchedLocationIdAsString\\n      searchedLocationSeoName\\n      searchedLocationType\\n      topCityIdsToNameResults {{\\n        key\\n        value\\n        __typename\\n      }}\\n      topEmployerIdsToNameResults {{\\n        key\\n        value\\n        __typename\\n      }}\\n      topEmployerNameResults\\n      topOccupationResults\\n      __typename\\n    }}\\n    totalJobsCount\\n    __typename\\n  }}\\n}}\\n\\nfragment JobView on JobListingSearchResult {{\\n  jobview {{\\n    header {{\\n      adOrderId\\n      advertiserType\\n      ageInDays\\n      divisionEmployerName\\n      easyApply\\n      employer {{\\n        id\\n        name\\n        shortName\\n        __typename\\n      }}\\n      organic\\n      employerNameFromSearch\\n      goc\\n      gocConfidence\\n      gocId\\n      isSponsoredJob\\n      isSponsoredEmployer\\n      jobCountryId\\n      jobLink\\n      jobResultTrackingKey\\n      normalizedJobTitle\\n      jobTitleText\\n      locationName\\n      locationType\\n      locId\\n      needsCommission\\n      payCurrency\\n      payPeriod\\n      payPeriodAdjustedPay {{\\n        p10\\n        p50\\n        p90\\n        __typename\\n      }}\\n      rating\\n      salarySource\\n      savedJobId\\n      seoJobLink\\n      __typename\\n    }}\\n    job {{\\n      descriptionFragments\\n      importConfigId\\n      jobTitleId\\n      jobTitleText\\n      listingId\\n      __typename\\n    }}\\n    jobListingAdminDetails {{\\n      cpcVal\\n      importConfigId\\n      jobListingId\\n      jobSourceId\\n      userEligibleForAdminJobDetails\\n      __typename\\n    }}\\n    overview {{\\n      shortName\\n      squareLogoUrl\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  __typename\\n}}\\n"}}]'
    response = requests.post(target_url, headers=headers, data=job_list_query)
    if response:
        return response.json()[1]["data"]["jobListings"]
    elif response.status_code == 502:
        return fetch_jobs_us(cursor)
    else:
        print("\n\n")
        print(f"HTTP Response: {response.status_code}\n Try again later.")
        return None


def fetch_jobs_ca(cursor: str) -> dict[Any] | None:
    """
    Returns a dictionary representing the JSON response for
    30 job postings in Canada and their generalized information.

    <cursor> is the pagination cursor for the current query.

    If an HTTP status of >= 300 is retrieved by the POST request,
    the specific HTTP status is printed and None is returned.
    """
    target_url = "https://www.glassdoor.ca/graph"
    headers = {
        "content-type": "application/json",
        "gd-csrf-token": "g1Pap2CLYOr1TlDIB7v_1w:BVvkWc1Czkiaae7GSEeK72VaaOmeSnPiMoU5Fv5z-J6bZkVxUHOBZ6o2lxrOBW362CjJXZ"
        "hj5oHDq2uFnyq8tA:TaaIXLlfr3qKo1E8EYjcg5mMXgl99BTp8s-c4hq1Lp0",
        "User-Agent": "",
    }
    job_list_query = f'[{{"operationName":"JobSearchResultsQuery","variables":{{"excludeJobListingIds":[],"filterParams":[],"keyword":"software internship","locationId":3,"locationType":"COUNTRY","numJobsToShow":30,"originalPageUrl":"https://www.glassdoor.ca/Job/canada-software-internship-jobs-SRCH_IL.0,6_IN3_KO7,26.htm","parameterUrlInput":"IL.0,6_IN3_KO7,26","pageType":"SERP","queryString":"","seoFriendlyUrlInput":"canada-software-internship-jobs","seoUrl":true,"includeIndeedJobAttributes":true,"pageCursor":"{cursor}","pageNumber":2}},"query":"query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String, $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String, $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean, $includeIndeedJobAttributes: Boolean) {{\\n  jobListings(\\n    contextHolder: {{queryString: $queryString, pageTypeEnum: $pageType, searchParams: {{excludeJobListingIds: $excludeJobListingIds, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, filterParams: $filterParams, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR, includeIndeedJobAttributes: $includeIndeedJobAttributes}}}}\\n  ) {{\\n    companyFilterOptions {{\\n      id\\n      shortName\\n      __typename\\n    }}\\n    filterOptions\\n    indeedCtk\\n    jobListings {{\\n      ...JobView\\n      __typename\\n    }}\\n    jobListingSeoLinks {{\\n      linkItems {{\\n        position\\n        url\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    jobSearchTrackingKey\\n    jobsPageSeoData {{\\n      pageMetaDescription\\n      pageTitle\\n      __typename\\n    }}\\n    paginationCursors {{\\n      cursor\\n      pageNumber\\n      __typename\\n    }}\\n    indexablePageForSeo\\n    searchResultsMetadata {{\\n      searchCriteria {{\\n        implicitLocation {{\\n          id\\n          localizedDisplayName\\n          type\\n          __typename\\n        }}\\n        keyword\\n        location {{\\n          id\\n          shortName\\n          localizedShortName\\n          localizedDisplayName\\n          type\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      footerVO {{\\n        countryMenu {{\\n          childNavigationLinks {{\\n            id\\n            link\\n            textKey\\n            __typename\\n          }}\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      helpCenterDomain\\n      helpCenterLocale\\n      jobAlert {{\\n        jobAlertExists\\n        __typename\\n      }}\\n      jobSerpFaq {{\\n        questions {{\\n          answer\\n          question\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      jobSerpJobOutlook {{\\n        occupation\\n        paragraph\\n        heading\\n        __typename\\n      }}\\n      showMachineReadableJobs\\n      __typename\\n    }}\\n    serpSeoLinksVO {{\\n      relatedJobTitlesResults\\n      searchedJobTitle\\n      searchedKeyword\\n      searchedLocationIdAsString\\n      searchedLocationSeoName\\n      searchedLocationType\\n      topCityIdsToNameResults {{\\n        key\\n        value\\n        __typename\\n      }}\\n      topEmployerIdsToNameResults {{\\n        key\\n        value\\n        __typename\\n      }}\\n      topEmployerNameResults\\n      topOccupationResults\\n      __typename\\n    }}\\n    totalJobsCount\\n    __typename\\n }}\\n}}\\n\\nfragment JobView on JobListingSearchResult {{\\n  jobview {{\\n    header {{\\n      indeedJobAttribute {{\\n        skills\\n        extractedJobAttributes {{\\n          key\\n          value\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      adOrderId\\n      advertiserType\\n      ageInDays\\n      divisionEmployerName\\n      easyApply\\n      employer {{\\n        id\\n        name\\n        shortName\\n        __typename\\n      }}\\n      organic\\n      employerNameFromSearch\\n      goc\\n      gocConfidence\\n      gocId\\n      isSponsoredJob\\n      isSponsoredEmployer\\n      jobCountryId\\n      jobLink\\n      jobResultTrackingKey\\n      normalizedJobTitle\\n      jobTitleText\\n      locationName\\n      locationType\\n      locId\\n      needsCommission\\n      payCurrency\\n      payPeriod\\n      payPeriodAdjustedPay {{\\n        p10\\n        p50\\n        p90\\n        __typename\\n      }}\\n      rating\\n      salarySource\\n      savedJobId\\n      seoJobLink\\n      __typename\\n    }}\\n    job {{\\n      descriptionFragments\\n      importConfigId\\n      jobTitleId\\n      jobTitleText\\n      listingId\\n      __typename\\n    }}\\n    jobListingAdminDetails {{\\n      cpcVal\\n      importConfigId\\n      jobListingId\\n      jobSourceId\\n      userEligibleForAdminJobDetails\\n      __typename\\n    }}\\n    overview {{\\n      shortName\\n      squareLogoUrl\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  __typename\\n}}\\n"}}]'
    response = requests.post(target_url, headers=headers, data=job_list_query)
    if response:
        return response.json()[0]["data"]["jobListings"]
    elif response.status_code == 502:
        return fetch_jobs_ca(cursor)
    else:
        print("\n\n")
        print(f"HTTP Response: {response.status_code}\n Try again later.")
        return None


# ====================================================================================
# Asynchronous Scraping Functions
# ====================================================================================


async def process_job_listings(jobs: list[Any], ids: set[int]) -> None:
    """
    Processes <jobs> by parsing detailed information from each job and storing
    necessary information into a csv file: jobs.csv.

    <jobs> is a list of up to 30 job postings, each with their generalized information represented
    as a dictionary which is parsed from a JSON response; and, <ids> is a list of unique job
    ids representing job postings which have already been processed.

    NOTE: This function is asyncronuous and fetches each job postings specific
    detailed information asyncronuously, significantly reducing the overall
    processing time by over 10 times as compared to syncronuous calls.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_job_details(
                session, int(j["jobview"]["jobListingAdminDetails"]["jobListingId"])
            )
            for j in jobs
        ]
        responses = await asyncio.gather(*tasks)

        for i in range(len(jobs)):
            job = jobs[i]
            job_specifics = responses[i]
            if job_specifics == {}:
                continue

            job_title = job["jobview"]["header"]["jobTitleText"]
            employer_name = job["jobview"]["header"]["employerNameFromSearch"]
            rating = job["jobview"]["header"]["rating"]
            link = job["jobview"]["header"]["seoJobLink"]
            fragmented_desc = job["jobview"]["job"]["descriptionFragments"]
            job_id = job["jobview"]["jobListingAdminDetails"]["jobListingId"]
            if job_id in ids:  # prevents duplicates
                continue
            skills = job_specifics["header"]["indeedJobAttribute"]["skillsLabel"]
            latitutde = job_specifics["map"]["lat"]
            longitude = job_specifics["map"]["lng"]
            city = job_specifics["map"]["cityName"]
            country = job_specifics["map"]["country"]
            full_desc = job_specifics["job"]["description"]
            ids.add(job_id)  #

            if job["jobview"]["header"]["payPeriod"] is not None:
                pay_period = job["jobview"]["header"]["payPeriod"]
                pay = job["jobview"]["header"]["payPeriodAdjustedPay"]["p50"]
            else:
                pay = randint(40000, 50000)
                pay_period = "ANNUAL"

            if not rating:
                rating = "0"

            if latitutde is None or not latitutde:
                latitutde = -3.14159
            if longitude is None or not longitude:
                longitude = -3.14159
            if not country:
                currency = job["jobview"]["header"]["payCurrency"]
                if currency == "CAD":
                    country = "Canada"
                else:
                    country = "United States"

            job_details = [
                job_title,
                employer_name,
                rating,
                link,
                fragmented_desc,
                skills,
                latitutde,
                longitude,
                city,
                country,
                pay_period,
                pay,
                job_id,
                full_desc,
            ]
            sanitize_details(job_details)
            write_csv("jobs.csv", job_details)


async def fetch_job_details(session: aiohttp.ClientSession, job_id: int) -> dict[Any]:
    """
    Returns a dictionary containing detailed specific information of the job posting
    associated with <job_id>.

    <session> is an asyncronuous session used for making HTTP requests; and <job_id>
    is the unique id representing the desired job posting whose information request.

    This function constructs and sends a POST request with a GraphQL query, retrieving
    detailed information in a JSON format, which is then parsed as a dictionary.

    Incase of an HTTP response >= 300, the function will retry sending a post request.
    """
    target_url = "https://www.glassdoor.ca/graph"
    headers = {
        "content-type": "application/json",
        "gd-csrf-token": "g1Pap2CLYOr1TlDIB7v_1w:BVvkWc1Czkiaae7GSEeK72VaaOmeSnPiMoU5Fv5z-J6bZkVxUHOBZ6o2lxrOBW362CjJXZ"
        "hj5oHDq2uFnyq8tA:TaaIXLlfr3qKo1E8EYjcg5mMXgl99BTp8s-c4hq1Lp0",
        "User-Agent": "",
    }
    job_query = f'[{{"operationName":"JobDetailQuery","variables":{{"enableReviewSummary":true,"jl":{job_id},"queryString":"pos=103&ao=1136043&s=58&guid=0000018e8d41a5119fabc43362077072&src=GD_JOB_AD&t=SR&vt=w&ea=1&cs=1_0b675c31&cb=1711766873784&jobListingId=1009198443079&jrtk=5-yul1-0-1hq6k39a8hdh9802-1de3e23b19ddcb90","pageTypeEnum":"SERP"}},"query":"query JobDetailQuery($jl: Long!, $queryString: String, $enableReviewSummary: Boolean!, $pageTypeEnum: PageTypeEnum) {{\\n  jobview: jobView(\\n    listingId: $jl\\n    contextHolder: {{queryString: $queryString, pageTypeEnum: $pageTypeEnum}}\\n  ) {{\\n    ...DetailFragment\\n    employerReviewSummary @include(if: $enableReviewSummary) {{\\n      reviewSummary {{\\n        highlightSummary {{\\n          sentiment\\n          sentence\\n          categoryReviewCount\\n          __typename\\n        }}\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n}}\\n\\nfragment DetailFragment on JobView {{\\n  employerBenefits {{\\n    benefitsOverview {{\\n      benefitsHighlights {{\\n        benefit {{\\n          commentCount\\n          icon\\n          name\\n          __typename\\n        }}\\n        highlightPhrase\\n        __typename\\n      }}\\n      overallBenefitRating\\n      employerBenefitSummary {{\\n        comment\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    benefitReviews {{\\n      benefitComments {{\\n        id\\n        comment\\n        __typename\\n      }}\\n      cityName\\n      createDate\\n      currentJob\\n      rating\\n      stateName\\n      userEnteredJobTitle\\n      __typename\\n    }}\\n    numReviews\\n    __typename\\n  }}\\n  employerContent {{\\n    featuredVideoLink\\n    managedContent {{\\n      id\\n      type\\n      title\\n      body\\n      captions\\n      photos\\n      videos\\n      __typename\\n    }}\\n    diversityContent {{\\n      goals {{\\n        id\\n        workPopulation\\n        underRepresentedGroup\\n        currentMetrics\\n        currentMetricsDate\\n        representationGoalMetrics\\n        representationGoalMetricsDate\\n        __typename\\n      }}\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  employerAttributes {{\\n    attributes {{\\n      attributeName\\n      attributeValue\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  gaTrackerData {{\\n    jobViewDisplayTimeMillis\\n    requiresTracking\\n    pageRequestGuid\\n    searchTypeCode\\n    trackingUrl\\n    __typename\\n  }}\\n  header {{\\n    jobLink\\n    adOrderId\\n    advertiserType\\n    ageInDays\\n    applicationId\\n    appliedDate\\n    applyUrl\\n    applyButtonDisabled\\n    blur\\n    coverPhoto {{\\n      url\\n      __typename\\n    }}\\n    divisionEmployerName\\n    easyApply\\n    easyApplyMethod\\n    employerNameFromSearch\\n    employer {{\\n      activeStatus\\n      bestProfile {{\\n        id\\n        __typename\\n      }}\\n      id\\n      name\\n      shortName\\n      size\\n      squareLogoUrl\\n      __typename\\n    }}\\n    expired\\n    goc\\n    hideCEOInfo\\n    indeedApplyMetadata\\n    indeedJobAttribute {{\\n      education\\n      skills\\n      educationLabel\\n      skillsLabel\\n      yearsOfExperienceLabel\\n      __typename\\n    }}\\n    isIndexableJobViewPage\\n    isSponsoredJob\\n    isSponsoredEmployer\\n    jobTitleText\\n    jobType\\n    jobTypeKeys\\n    jobCountryId\\n    jobResultTrackingKey\\n    locId\\n    locationName\\n    locationType\\n    needsCommission\\n    normalizedJobTitle\\n    organic\\n    payCurrency\\n    payPeriod\\n    payPeriodAdjustedPay {{\\n      p10\\n      p50\\n      p90\\n      __typename\\n    }}\\n    rating\\n    remoteWorkTypes\\n    salarySource\\n    savedJobId\\n    seoJobLink\\n    serpUrlForJobListing\\n    sgocId\\n    categoryMgocId\\n    urgencySignal {{\\n      labelKey\\n      messageKey\\n      normalizedCount\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  similarJobs {{\\n    relatedJobTitle\\n    careerUrl\\n    __typename\\n  }}\\n  job {{\\n    description\\n    discoverDate\\n    eolHashCode\\n    importConfigId\\n    jobReqId\\n    jobSource\\n    jobTitleId\\n    jobTitleText\\n    listingId\\n    __typename\\n  }}\\n  jobListingAdminDetails {{\\n    adOrderId\\n    cpcVal\\n    importConfigId\\n    jobListingId\\n    jobSourceId\\n    userEligibleForAdminJobDetails\\n    __typename\\n  }}\\n  map {{\\n    address\\n    cityName\\n    country\\n    employer {{\\n      id\\n      name\\n      __typename\\n    }}\\n    lat\\n    lng\\n    locationName\\n    postalCode\\n    stateName\\n    __typename\\n  }}\\n  overview {{\\n    ceo {{\\n      name\\n      photoUrl\\n      __typename\\n    }}\\n    id\\n    name\\n    shortName\\n    squareLogoUrl\\n    headquarters\\n    links {{\\n      overviewUrl\\n      benefitsUrl\\n      photosUrl\\n      reviewsUrl\\n      salariesUrl\\n      __typename\\n    }}\\n    primaryIndustry {{\\n      industryId\\n      industryName\\n      sectorName\\n      sectorId\\n      __typename\\n    }}\\n    ratings {{\\n      overallRating\\n      ceoRating\\n      ceoRatingsCount\\n      recommendToFriendRating\\n      compensationAndBenefitsRating\\n      cultureAndValuesRating\\n      careerOpportunitiesRating\\n      seniorManagementRating\\n      workLifeBalanceRating\\n      __typename\\n    }}\\n    revenue\\n    size\\n    sizeCategory\\n    type\\n    website\\n    yearFounded\\n    __typename\\n  }}\\n  photos {{\\n    photos {{\\n      caption\\n      photoId\\n      photoId2x\\n      photoLink\\n      photoUrl\\n      photoUrl2x\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  reviews {{\\n    reviews {{\\n      advice\\n      cons\\n      countHelpful\\n      employerResponses {{\\n        response\\n        responseDateTime\\n        userJobTitle\\n        __typename\\n      }}\\n      employmentStatus\\n      featured\\n      isCurrentJob\\n      jobTitle {{\\n        text\\n        __typename\\n      }}\\n      lengthOfEmployment\\n      pros\\n      ratingBusinessOutlook\\n      ratingCareerOpportunities\\n      ratingCeo\\n      ratingCompensationAndBenefits\\n      ratingCultureAndValues\\n      ratingOverall\\n      ratingRecommendToFriend\\n      ratingSeniorLeadership\\n      ratingWorkLifeBalance\\n      reviewDateTime\\n      reviewId\\n      summary\\n      __typename\\n    }}\\n    __typename\\n  }}\\n  __typename\\n}}\\n"}}]'
    async with session.post(
        target_url, headers=headers, data=job_query, ssl=False
    ) as response:
        data = await response.text()
        if response.status >= 300:
            return await fetch_job_details(session, job_id)
        data = json.loads(data)
        return data[0]["data"]["jobview"]


# ====================================================================================
# Main Function
# ====================================================================================
if __name__ == "__main__":
    scrape()
    import python_ta

    # NOTES FOR PYTHON-TA:
    # 2. E9998 (Forbidden-IO-Function): Necessary as to communicate scraping status, incase of ratelimiting.
    # 3. C0301 (Line-Too-Long): Necessary to query Glassdoor's GraphQL.
    # 4. R0914 (Too-Many-Locals): Necessary to save all data we scraped and to do it in one function
    #                             for easier readability and cleanliness.

    # NOTE: To avoid inherent bugs related to csv.writer() and file locking, do not have jobs.csv open while
    # running this.

    python_ta.check_all(
        config={
            "max-line-length": 120,
            "extra-imports": [
                "csv",
                "random",
                "requests",
                "time",
                "asyncio",
                "aiohttp",
                "json",
                "utility",
            ],
            "disable": ["E9998", "C0301", "R0914"],
        }
    )
