import { MigrationInterface, QueryRunner } from "typeorm";

export class Tasks1765361646943 implements MigrationInterface {
    name = 'Tasks1765361646943'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TYPE "public"."tasks_difficulty_enum" AS ENUM('LOW', 'MEDIUM', 'HIGH')`);
        await queryRunner.query(`CREATE TYPE "public"."tasks_status_enum" AS ENUM('READY', 'IN_PROGRESS', 'COMPLETED')`);
        await queryRunner.query(`CREATE TABLE "tasks" ("id" BIGSERIAL NOT NULL, "title" character varying(70) NOT NULL, "description" character varying NOT NULL, "assignee_id" bigint, "story_points" integer, "sprint" character varying, "deadline" date, "project_id" bigint, "difficulty" "public"."tasks_difficulty_enum" NOT NULL DEFAULT 'MEDIUM', "status" "public"."tasks_status_enum" NOT NULL DEFAULT 'READY', "assigned_by" bigint NOT NULL, CONSTRAINT "PK_8d12ff38fcc62aaba2cab748772" PRIMARY KEY ("id"))`);
        await queryRunner.query(`ALTER TABLE "tasks" ADD CONSTRAINT "FK_9eecdb5b1ed8c7c2a1b392c28d4" FOREIGN KEY ("project_id") REFERENCES "projects"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
        await queryRunner.query(`ALTER TABLE "tasks" ADD CONSTRAINT "FK_a8a7b3b66c0b0fee5da777fea96" FOREIGN KEY ("assigned_by") REFERENCES "managers"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
        await queryRunner.query(`ALTER TABLE "tasks" ADD CONSTRAINT "FK_855d484825b715c545349212c7f" FOREIGN KEY ("assignee_id") REFERENCES "users"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`ALTER TABLE "tasks" DROP CONSTRAINT "FK_855d484825b715c545349212c7f"`);
        await queryRunner.query(`ALTER TABLE "tasks" DROP CONSTRAINT "FK_a8a7b3b66c0b0fee5da777fea96"`);
        await queryRunner.query(`ALTER TABLE "tasks" DROP CONSTRAINT "FK_9eecdb5b1ed8c7c2a1b392c28d4"`);
        await queryRunner.query(`DROP TABLE "tasks"`);
        await queryRunner.query(`DROP TYPE "public"."tasks_status_enum"`);
        await queryRunner.query(`DROP TYPE "public"."tasks_difficulty_enum"`);
    }

}
