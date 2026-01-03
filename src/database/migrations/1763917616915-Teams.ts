import { MigrationInterface, QueryRunner } from "typeorm";

export class Teams1763917616915 implements MigrationInterface {
    name = 'Teams1763917616915'

    public async up(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`CREATE TABLE "teams" ("id" BIGSERIAL NOT NULL, "team_name" character varying(70) NOT NULL, "manager_id" bigint NOT NULL, CONSTRAINT "PK_7e5523774a38b08a6236d322403" PRIMARY KEY ("id"))`);
        await queryRunner.query(`ALTER TABLE "teams" ADD CONSTRAINT "FK_9a06e17b915db57b2d9192672a5" FOREIGN KEY ("manager_id") REFERENCES "managers"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        await queryRunner.query(`ALTER TABLE "teams" DROP CONSTRAINT "FK_9a06e17b915db57b2d9192672a5"`);
        await queryRunner.query(`DROP TABLE "teams"`);
    }

}
